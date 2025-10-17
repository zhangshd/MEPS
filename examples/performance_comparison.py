"""
Performance Comparison Visualization
Illustrates the time savings from parallel monomer optimization
Author: zhangshd
Date: 2025-10-17
"""

import matplotlib.pyplot as plt
import numpy as np

def create_comparison_chart():
    """
    Create a visual comparison of sequential vs parallel optimization times
    """
    
    # Test scenarios
    scenarios = [
        ('Small molecules\n(Benzene + Water)', 0.5, 0.3),
        ('Medium molecules\n(Drug-like)', 3.0, 2.0),
        ('Large molecules\n(Protein fragments)', 8.0, 8.0)
    ]
    
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 6))
    
    # Left plot: Time breakdown
    x_pos = np.arange(len(scenarios))
    width = 0.35
    
    sequential_times = []
    parallel_times = []
    
    for name, time_a, time_b in scenarios:
        sequential_times.append(time_a + time_b)
        parallel_times.append(max(time_a, time_b))
    
    bars1 = ax1.bar(x_pos - width/2, sequential_times, width, 
                     label='Sequential', color='#FF6B6B', alpha=0.8)
    bars2 = ax1.bar(x_pos + width/2, parallel_times, width,
                     label='Parallel', color='#4ECDC4', alpha=0.8)
    
    ax1.set_xlabel('Scenario', fontsize=12, fontweight='bold')
    ax1.set_ylabel('Total Time (hours)', fontsize=12, fontweight='bold')
    ax1.set_title('Sequential vs Parallel Optimization Time', 
                   fontsize=14, fontweight='bold', pad=20)
    ax1.set_xticks(x_pos)
    ax1.set_xticklabels([s[0] for s in scenarios])
    ax1.legend(fontsize=11)
    ax1.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels on bars
    for bars in [bars1, bars2]:
        for bar in bars:
            height = bar.get_height()
            ax1.text(bar.get_x() + bar.get_width()/2., height,
                    f'{height:.1f}h',
                    ha='center', va='bottom', fontsize=10, fontweight='bold')
    
    # Right plot: Speedup factors
    speedups = [seq/par for seq, par in zip(sequential_times, parallel_times)]
    colors = ['#4ECDC4' if s >= 1.5 else '#FFE66D' for s in speedups]
    
    bars3 = ax2.bar(x_pos, speedups, color=colors, alpha=0.8, edgecolor='black', linewidth=1.5)
    ax2.axhline(y=1.0, color='red', linestyle='--', linewidth=2, label='No speedup', alpha=0.7)
    ax2.axhline(y=2.0, color='green', linestyle='--', linewidth=2, label='2x speedup', alpha=0.7)
    
    ax2.set_xlabel('Scenario', fontsize=12, fontweight='bold')
    ax2.set_ylabel('Speedup Factor', fontsize=12, fontweight='bold')
    ax2.set_title('Parallel Optimization Speedup', 
                   fontsize=14, fontweight='bold', pad=20)
    ax2.set_xticks(x_pos)
    ax2.set_xticklabels([s[0] for s in scenarios])
    ax2.set_ylim(0, 2.5)
    ax2.legend(fontsize=11)
    ax2.grid(axis='y', alpha=0.3, linestyle='--')
    
    # Add value labels
    for i, (bar, speedup) in enumerate(zip(bars3, speedups)):
        height = bar.get_height()
        ax2.text(bar.get_x() + bar.get_width()/2., height,
                f'{speedup:.2f}x',
                ha='center', va='bottom', fontsize=11, fontweight='bold')
        
        # Add time saved percentage
        time_saved = (1 - 1/speedup) * 100
        ax2.text(bar.get_x() + bar.get_width()/2., height/2,
                f'Save\n{time_saved:.0f}%',
                ha='center', va='center', fontsize=9, 
                color='white', fontweight='bold')
    
    plt.tight_layout()
    plt.savefig('parallel_optimization_comparison.png', dpi=300, bbox_inches='tight')
    plt.show()
    
    print("Chart saved as 'parallel_optimization_comparison.png'")


def print_time_table():
    """
    Print a detailed comparison table
    """
    print("\n" + "="*80)
    print("PARALLEL OPTIMIZATION PERFORMANCE COMPARISON")
    print("="*80)
    
    scenarios = [
        ('Small molecules (Benzene + Water)', 0.5, 0.3),
        ('Medium molecules (Drug-like)', 3.0, 2.0),
        ('Large molecules (Protein fragments)', 8.0, 8.0)
    ]
    
    print("\n{:<40} {:>12} {:>12} {:>12} {:>12}".format(
        "Scenario", "Monomer A", "Monomer B", "Sequential", "Parallel"
    ))
    print("-" * 80)
    
    for name, time_a, time_b in scenarios:
        seq_time = time_a + time_b
        par_time = max(time_a, time_b)
        speedup = seq_time / par_time
        time_saved = seq_time - par_time
        
        print("{:<40} {:>10.1f}h {:>10.1f}h {:>10.1f}h {:>10.1f}h".format(
            name, time_a, time_b, seq_time, par_time
        ))
        print("{:<40} {:>12} {:>12} {:>12} {:>12}".format(
            "", "", "", 
            f"Speedup: {speedup:.2f}x", 
            f"Save: {time_saved:.1f}h"
        ))
        print()


def calculate_resource_requirements():
    """
    Calculate and display resource requirements for parallel execution
    """
    print("\n" + "="*80)
    print("RESOURCE REQUIREMENTS FOR PARALLEL OPTIMIZATION")
    print("="*80)
    
    configs = [
        ("Conservative (Small molecules)", 32, 30),
        ("Moderate (Medium molecules)", 48, 50),
        ("Intensive (Large molecules)", 96, 100)
    ]
    
    print("\n{:<35} {:>15} {:>15} {:>15}".format(
        "Configuration", "Cores/Job", "Total Cores", "Total Memory"
    ))
    print("-" * 80)
    
    for name, cores_per_job, mem_per_job in configs:
        total_cores = cores_per_job * 2
        total_mem = mem_per_job * 2
        
        print("{:<35} {:>15} {:>15} {:>15}".format(
            name, 
            cores_per_job, 
            f"{total_cores} (2 jobs)",
            f"{total_mem}GB (2 jobs)"
        ))
    
    print("\n" + "="*80)
    print("RECOMMENDATION:")
    print("  - Leave 10-20% system resources for OS and other processes")
    print("  - For 96-core system: use nproc=48 per job")
    print("  - For 200GB RAM system: use mem='90GB' per job")
    print("="*80)


if __name__ == "__main__":
    print("Generating parallel optimization comparison...")
    
    # Print detailed tables
    print_time_table()
    calculate_resource_requirements()
    
    # Create visualization
    create_comparison_chart()
    
    print("\nAnalysis complete!")
