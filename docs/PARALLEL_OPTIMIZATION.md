# Parallel Monomer Optimization

## Overview

This document explains the parallel optimization improvements made to the `gaussian_runner.py` module to enhance computational efficiency.

## Problem Analysis

### Original Sequential Logic

In the original implementation, monomer molecules were optimized sequentially:

```
Time ──────────────────────────────────────────────────────>

Monomer A Optimization: [████████████████] (e.g., 2 hours)
                                           Monomer B Optimization: [████████████████] (e.g., 2 hours)
                                                                                      Complex...

Total Time: 4+ hours
```

**Issues:**
- Monomer A and B optimizations are **independent** tasks
- Sequential execution wastes time when both could run simultaneously
- Total pipeline time unnecessarily long

### Improved Parallel Logic

With the new parallel implementation:

```
Time ──────────────────────────────>

Monomer A Optimization: [████████████████] (2 hours)
Monomer B Optimization: [████████████████] (2 hours)
                                           Complex...

Total Time: 2+ hours (50% time saved!)
```

## Implementation Details

### Key Changes

1. **Added `concurrent.futures` import**
   - Provides thread-based parallelism for I/O-bound tasks (monitoring calculations)

2. **New method: `wait_for_calculations()`**
   - Monitors multiple Gaussian calculations simultaneously
   - Returns status dictionary for all calculations
   - Supports timeout and custom check intervals

3. **New method: `optimize_monomers_parallel()`**
   - Accepts list of (structure, name) tuples
   - Submits all optimizations with `wait=False`
   - Waits for all calculations to complete
   - Reports individual success/failure status

4. **Modified `run_full_pipeline()`**
   - Replaces two sequential `optimize_monomer()` calls
   - Uses single `optimize_monomers_parallel()` call
   - Automatically extracts results for both monomers

### Code Example

```python
# Original sequential approach
monomer_a_files = pipeline.optimize_monomer(struct_a, "mol_a")  # Wait
monomer_b_files = pipeline.optimize_monomer(struct_b, "mol_b")  # Wait

# New parallel approach
monomer_files = pipeline.optimize_monomers_parallel(
    structures=[(struct_a, "mol_a"), (struct_b, "mol_b")]
)
monomer_a_files = monomer_files[0]
monomer_b_files = monomer_files[1]
```

## Technical Considerations

### Why Not Use ProcessPoolExecutor?

The current implementation uses background Gaussian processes rather than Python multiprocessing:
- Gaussian itself runs as separate process
- We just need to monitor multiple output files
- ThreadPoolExecutor (future enhancement) or simple polling works well
- Avoids Python GIL limitations

### Resource Management

**Important**: When running parallel optimizations, be aware of:

1. **CPU Resources**: Each monomer uses `nproc` cores
   - Running 2 monomers with `nproc=96` requires 192 total cores
   - Adjust `nproc` accordingly: use `nproc=48` per job on a 96-core system

2. **Memory Resources**: Each calculation uses `mem` memory
   - Running 2 jobs with `mem="100GB"` requires 200GB total
   - Adjust memory allocation based on available RAM

3. **Disk I/O**: Both calculations write checkpoint files
   - Ensure sufficient disk space for multiple .chk files
   - Fast storage (SSD) recommended for better performance

### Best Practices

```python
# For a 96-core, 200GB RAM system running 2 parallel monomers
results = pipeline.run_full_pipeline(
    molecule_a_file="mol_a.xyz",
    molecule_b_file="mol_b.xyz",
    nproc=48,      # 48 cores per job (total: 96)
    mem="90GB",    # 90GB per job (total: 180GB, leave 20GB for system)
    functional="B3LYP",
    basis_set="6-311++G(d,p)"
)
```

## Performance Gains

### Time Savings

Assuming:
- Monomer A optimization: T_A
- Monomer B optimization: T_B

**Sequential time**: T_total = T_A + T_B

**Parallel time**: T_total = max(T_A, T_B)

**Speedup**: 
- If T_A ≈ T_B: ~2x faster (50% time saved)
- If T_A ≠ T_B: speedup = (T_A + T_B) / max(T_A, T_B)

### Real-world Example

| Molecule | Atoms | Sequential Time | Parallel Time | Speedup |
|----------|-------|----------------|---------------|---------|
| Benzene + Water | 12 + 3 | 0.5h + 0.3h = 0.8h | max(0.5, 0.3) = 0.5h | 1.6x |
| Drug + Protein fragment | 50 + 30 | 3h + 2h = 5h | max(3, 2) = 3h | 1.67x |
| Large complex molecules | 100 + 100 | 8h + 8h = 16h | max(8, 8) = 8h | 2.0x |

## Error Handling

The parallel implementation includes robust error handling:

1. **Individual failure tracking**: If one monomer fails, you still get results for the other
2. **Clear error reporting**: Each calculation's status is reported separately
3. **No cascading failures**: One failure doesn't prevent other calculations from completing

Example output:
```
Parallel optimization results:
  - benzene: Success
  - clopidol: Failed
    Error: SCF convergence failure after 512 cycles
```

## Future Enhancements

Potential improvements for even better performance:

1. **Extend to complex optimization**: Currently only monomers are parallel
2. **Dynamic resource allocation**: Automatically adjust nproc based on available cores
3. **Queue management**: Support for >2 molecules with resource-aware scheduling
4. **Async I/O**: Use asyncio for more efficient file monitoring
5. **Remote execution**: Distribute calculations across multiple compute nodes

## API Reference

### `wait_for_calculations(log_files, check_interval=60, timeout=None)`

Monitor multiple Gaussian calculations simultaneously.

**Parameters:**
- `log_files` (List[str]): List of output file paths to monitor
- `check_interval` (int): Check interval in seconds (default: 60)
- `timeout` (Optional[int]): Timeout in seconds, None for no timeout

**Returns:**
- Dict[str, bool]: Dictionary mapping log file paths to success status

### `optimize_monomers_parallel(structures, functional, basis_set, dispersion, mem, nproc)`

Optimize multiple monomer molecules in parallel.

**Parameters:**
- `structures` (List[Tuple[StructureParser, str]]): List of (structure, name) tuples
- `functional` (str): DFT functional (default: "B3LYP")
- `basis_set` (str): Basis set (default: "6-311++G(d,p)")
- `dispersion` (str): Dispersion correction (default: "GD3BJ")
- `mem` (str): Memory allocation (default: "100GB")
- `nproc` (int): Number of CPU cores per calculation (default: 96)

**Returns:**
- List[Dict[str, str]]: List of file path dictionaries for each monomer

## Conclusion

The parallel optimization implementation significantly improves the efficiency of the MEPS pipeline by eliminating unnecessary wait times during independent monomer calculations. This is especially beneficial for:

- Large-scale screening studies
- High-throughput computational workflows
- Research projects with limited computational time budgets

The implementation maintains backward compatibility while providing automatic performance improvements to all users of the `run_full_pipeline()` method.
