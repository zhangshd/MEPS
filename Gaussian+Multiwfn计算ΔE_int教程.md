

# **使用Gaussian和Multiwfn计算与分析分子间相互作用能的综合指南**

## **引言**

### **分子间相互作用的核心地位**

非共价相互作用是贯穿所有化学科学分支的基本驱动力，从药物设计、共晶工程 1 到超分子化学和材料科学，其影响无处不在。深刻理解这些作用力是准确预测分子聚集行为、化学反应性及功能的关键。

### **稳定性的量化：相互作用能（ΔEint）**

相互作用能（Interaction Energy, ）是衡量分子复合物热力学稳定性的核心指标。根据热力学惯例， 的负值表示复合物相对于其孤立组分是稳定的，且其绝对值越大，相互作用越强 3。

### **协同分析工作流**

本报告的核心是介绍一种协同分析方法：首先，使用量子化学程序Gaussian进行严谨的、定量的能量计算；其次，利用波函数分析软件Multiwfn进行定性的、解释性的分析。必须强调，单一的能量数值虽然必要，但对于获得深刻的化学洞见而言是远远不够的；我们还必须探究相互作用的*本质* 4。因此，本指南将展示一个完整的工作流程：Gaussian提供“是什么”（复合物有多稳定？）的答案，而Multiwfn则揭示“为什么”（是什么作用力主导了这种稳定？）。

## **第一节：相互作用能计算的理论框架**

### **1.1 超分子方法：基本定义**

相互作用能（ΔEint​）通常通过超分子方法进行计算，其基本公式定义如下 3：

其中，Ecomplex​ 是相互作用复合物（二聚体）的总电子能量，EmonomerA​ 和 EmonomerB​ 分别是经过结构优化的孤立单体A和B的能量。该公式构成了第三节中实际计算的基础。

### **1.2 重叠校正的必要性：揭示基组重叠误差（BSSE）**

在量子化学计算中，使用有限的基组是对真实波函数的一种近似描述 5。当两个单体（A和B）相互靠近形成复合物时，一个被称为“基函数借用”的现象便会发生：单体A可以“借用”单体B的基函数来更精确地描述自身的电子密度，反之亦然 7。这种现象并非真实的物理效应，而是一种由基组不完备性导致的数学赝象。

这种赝象的因果链条非常明确：不完备的基组 → 基函数借用 → 复合物被人为地额外稳定 → 相互作用能被高估（即$\\Delta E\_{int}$的计算结果过于负）→ 得出错误的化学结论 7。这种计算误差被称为基组重叠误差（Basis Set Superposition Error, BSSE）。

因此，计算出的BSSE值不仅仅是一个需要从总能量中减去的数字，它更是一个关于所选基组是否充分的关键诊断指标。一个异常大的BSSE值（例如，大于 2-3 kcal/mol）应当引起研究者的高度警惕，因为它暗示所选的基组对于当前研究的体系可能不够完备。在这种情况下，即使经过校正，所得出的结果也应谨慎对待。因此，在计算过程中，不仅要应用校正，还应报告BSSE的大小，并思考其对理论水平选择的启示，这有助于将计算者从单纯的操作者提升为具有批判性思维的分析者。

### **1.3 Boys & Bernardi方法：黄金标准校正方案**

由Boys和Bernardi提出的反向校正（Counterpoise, CP）方法是消除BSSE的标准且最可靠的方案 7。CP方法的核心原则是确保计算的“平衡性”，即单体的能量必须在与整个复合物完全相同的基组下进行计算。

为了实现这一点，引入了“鬼原子”（ghost atoms）的概念。鬼原子是指在空间中定义了一个中心，该中心拥有基函数，但没有原子核，也没有电子 7。这是诸如Gaussian等软件计算单体A在二聚体基组下的能量（记为）的实际机制。

经过CP校正的相互作用能公式如下，它与未校正的公式形成对比，逻辑更为严谨 7：

## **第二节：选择合适的理论水平**

### **2.1 适用于非共价相互作用的密度泛函选择**

标准的密度泛函（如早期的B3LYP）主要为共价体系开发，在描述非共价复合物中占主导地位的长程色散力（范德华力）方面存在严重缺陷 13。因此，必须使用包含经验色散校正的泛函。目前广泛应用且性能优异的包括Grimme提出的D3或D3(BJ)校正方案 13。

经过大量基准测试验证的、值得推荐的泛函家族包括：Minnesota泛函家族（如M06-2X）、长程校正泛函（如ωB97X-D）以及双杂化泛函（如B2PLYP-D3） 13。此外，流行的B3LYP泛函与D3校正的组合（B3LYP-D3）也被证明是一种兼具可靠性和计算效率的选择 16。

### **2.2 基组的关键作用**

基组的质量与BSSE的大小直接相关。高质量的基组可以最小化（但通常无法完全消除）BSSE。对于非共价相互作用的计算，基组的选择尤为重要。

**极化函数**（例如，6-31G(d)中的“d”）对于描述分子相互作用时电子云的各向异性形变至关重要。

**弥散函数**（例如，6-31+G(d)中的“+”或aug-cc-pVDZ中的“aug-”）对于非共价相互作用的计算是**必不可少**的。这些函数在空间上分布范围很广，能够有效描述分子间区域束缚较弱的电子 16。

在实践中，Pople风格的基组如 6-311++G(d,p) 提供了良好的精度与成本平衡；Dunning相关的相关一致性基组如 aug-cc-pVTZ 更加稳健但计算成本更高；而Ahlrichs开发的 def2-TZVP 或 def2-TZVPD 则是现代计算中表现优异的替代方案 17。

### **表1：非共价相互作用计算的推荐理论水平组合**

下表总结了不同计算需求下的推荐理论水平组合，旨在帮助用户根据体系大小和可用计算资源做出明智选择。

| 级别 | 推荐泛函 | 推荐基组 | 应用场景与说明 |
| :---- | :---- | :---- | :---- |
| **经济高效型** | B3LYP-D3(BJ), ωB97X-D | 6-311++G(d,p), def2-TZVP | 适用于较大体系的初步筛选和常规计算，在成本和精度之间取得良好平衡 16。 |
| **稳健可靠型** | M06-2X, ωB97X-D | def2-TZVPD, aug-cc-pVTZ | 提供更高的精度，适用于中等大小体系的可靠能量计算和几何优化 13。 |
| **高精度基准型** | B2PLYP-D3(BJ), CCSD(T) | aug-cc-pVTZ, aug-cc-pVQZ | 用于小型二聚体的基准研究，或在需要极高精度时对较低级别理论的结果进行验证。 |

## **第三节：实践教程：使用Gaussian计算苯-甲烷复合物的ΔEint**

### **3.1 工作流程概述**

计算相互作用能需要执行以下三个核心步骤：

1. 优化单体A（苯）的几何结构。  
2. 优化单体B（甲烷）的几何结构。  
3. 基于优化后的单体结构，构建复合物，并对其执行一次性的Counterpoise能量计算。

### **3.2 步骤一：单体的几何优化**

首先，需要分别对苯和甲烷进行结构优化和频率分析。频率分析用于确认优化得到的结构是真实的能量极小点（没有虚频）。

**苯（Benzene）的Gaussian输入文件 (benzene.gjf)：**

代码段

%chk=benzene.chk  
%mem=4GB  
%nproc=8  
\#p opt freq B3LYP-D3(BJ)/6-311++G(d,p)

Benzene Optimization

0 1  
 C   \-1.211021    0.699188    0.000000  
 C   \-1.211021   \-0.699188    0.000000  
 C    0.000000   \-1.398376    0.000000  
 C    1.211021   \-0.699188    0.000000  
 C    1.211021    0.699188    0.000000  
 C    0.000000    1.398376    0.000000  
 H   \-2.152500    1.242761    0.000000  
 H   \-2.152500   \-1.242761    0.000000  
 H    0.000000   \-2.485522    0.000000  
 H    2.152500   \-1.242761    0.000000  
 H    2.152500    1.242761    0.000000  
 H    0.000000    2.485522    0.000000

**甲烷（Methane）的Gaussian输入文件 (methane.gjf)：**

代码段

%chk=methane.chk  
%mem=4GB  
%nproc=8  
\#p opt freq B3LYP-D3(BJ)/6-311++G(d,p)

Methane Optimization

0 1  
 C    0.000000    0.000000    0.000000  
 H    0.000000    0.000000    1.089000  
 H    1.026720    0.000000   \-0.363000  
 H   \-0.513360   \-0.889165   \-0.363000  
 H   \-0.513360    0.889165   \-0.363000

提交计算后，从输出文件（.log）的末尾找到“SCF Done:”一行，记录其能量值。

### **3.3 步骤二：构建二聚体复合物**

使用分子可视化软件（如GaussView）或文本编辑器，将优化后的苯和甲烷的坐标合并到一个文件中。在本例中，我们将甲烷置于苯环平面的上方，构成一个T形的π-堆积构型。

### **3.4 步骤三：最终的Counterpoise计算**

这是整个教程的核心步骤。以下是用于计算BSSE校正后相互作用能的最终输入文件。

**苯-甲烷复合物的Gaussian输入文件 (complex\_cp.gjf)：**

代码段

%chk=complex\_cp.chk  
%mem=8GB  
%nproc=16  
\#p B3LYP-D3(BJ)/6-311++G(d,p) Counterpoise=2

Benzene-Methane Complex, Counterpoise Calculation

0 1 0 1 0 1  
 C(Fragment=1)   \-1.211021    0.699188    0.000000  
 C(Fragment=1)   \-1.211021   \-0.699188    0.000000  
 C(Fragment=1)    0.000000   \-1.398376    0.000000  
 C(Fragment=1)    1.211021   \-0.699188    0.000000  
 C(Fragment=1)    1.211021    0.699188    0.000000  
 C(Fragment=1)    0.000000    1.398376    0.000000  
 H(Fragment=1)   \-2.152500    1.242761    0.000000  
 H(Fragment=1)   \-2.152500   \-1.242761    0.000000  
 H(Fragment=1)    0.000000   \-2.485522    0.000000  
 H(Fragment=1)    2.152500   \-1.242761    0.000000  
 H(Fragment=1)    2.152500    1.242761    0.000000  
 H(Fragment=1)    0.000000    2.485522    0.000000  
 C(Fragment=2)    0.000000    0.000000    3.500000  
 H(Fragment=2)    0.000000    0.000000    4.589000  
 H(Fragment=2)    1.026720    0.000000    3.137000  
 H(Fragment=2)   \-0.513360   \-0.889165    3.137000  
 H(Fragment=2)   \-0.513360    0.889165    3.137000

**关键输入行解释：**

* \#p... Counterpoise=2: 该行指示Gaussian执行一个包含两个片段的Counterpoise计算。  
* 0 1 0 1 0 1: 这是电荷和自旋多重度行，格式为：总电荷, 总多重度, 片段1电荷, 片段1多重度, 片段2电荷, 片段2多重度。对于中性、单重态的苯-甲烷体系，所有值均为0和1 20。  
* Atom(Fragment=N): 在坐标部分，每个原子都必须通过 (Fragment=N) 语法明确指定其所属的片段。这里，所有苯的原子被指定为片段1，所有甲烷的原子被指定为片段2 20。

### **3.5 步骤四：解读Gaussian输出并获得最终ΔEint**

计算完成后，在输出文件（.log）的末尾可以找到一个总结性的能量报告 20。

**典型的输出片段：**

 Counterpoise corrected energy \=    \-273.123456789012  
 BSSE energy \=       0.000987654321  
 sum of fragments \=    \-273.120012345678  
 complexation energy \=       \-2.16 kcal/mole (raw)  
 complexation energy \=       \-1.54 kcal/mole (corrected)

**输出解读：**

* Counterpoise corrected energy: 经过CP校正的复合物总能量。  
* BSSE energy: BSSE的大小（单位为Hartree）。这个值的大小可以反映基组的完备性。  
* complexation energy \=... (raw): 未经校正的相互作用能，这个值因BSSE的存在而是不准确的。  
* complexation energy \=... (corrected): **这是用户最终需要寻找和报告的、可靠的相互作用能$\\Delta E\_{int}$**。在本例中，苯和甲烷之间的相互作用能为-1.54 kcal/mol。

## **第四节：解构相互作用：使用Multiwfn进行定性分析**

### **4.1 从能量到洞见：波函数分析的准备**

量化计算给出了相互作用的强度，但要理解其本质，必须进行波函数分析以获得“物理洞见” 4。Multiwfn是执行此类分析的强大工具。

首先，需要将Gaussian计算得到的二进制检查点文件（.chk）转换为Multiwfn可以读取的格式化检查点文件（.fchk）。这可以通过Gaussian自带的formchk工具完成。在命令行中执行以下命令：  
formchk complex\_cp.chk complex\_cp.fchk

### **4.2 使用NCI（非共价相互作用）图可视化弱相互作用**

NCI分析能够以图形化的方式直观地展示分子中存在弱相互作用的区域和类型 23。

**Multiwfn中的操作命令：**

1. 启动Multiwfn，加载complex\_cp.fchk文件。  
2. 在主菜单中输入 20，选择“弱相互作用的可视化研究”。  
3. 输入 1，选择“常规NCI分析”。  
4. 选择格点质量，例如输入 3 代表高质量。  
5. 输入 3，生成用于可视化的cube文件（func1.cub 和 func2.cub）。

结果解读：  
NCI分析会生成不同颜色的等值面，其颜色由电子密度Hessian矩阵的第二特征值（λ2​）的符号与电子密度（ρ）的乘积决定 24。

* **蓝色等值面**: 表示强的、吸引性相互作用，如氢键。通常出现在  为较大负值的区域。  
* **绿色等值面**: 表示弱的、吸引性相互作用，如范德华力和π-π堆积。通常出现在  为接近零的负值区域。  
* **红色等值面**: 表示强的、排斥性相互作用，如空间位阻。通常出现在  为较大正值的区域。

对于苯-甲烷复合物，预计会在甲烷的氢原子与苯环之间观察到一片绿色的等值面，直观地证实了范德华相互作用的存在。

### **4.3 使用QTAIM（分子中的原子理论）表征化学键**

Bader提出的QTAIM理论通过分析电子密度的拓扑性质，为定义原子和化学键提供了严谨的理论框架 23。

Multiwfn中的操作命令 23：

1. 启动Multiwfn，加载complex\_cp.fchk文件。  
2. 在主菜单中输入 2，选择“拓扑分析”。  
3. 依次输入 2 和 3，从原子核位置和原子对中点开始搜索临界点（Critical Points, CPs）。  
4. 输入 8 然后输入 9，生成键径（bond paths）。  
5. 输入 0，可视化并打印CP信息。

结果解读：  
分析的重点是位于两个分子之间的（3, \-1）型键临界点（Bond Critical Point, BCP）。BCP处的电子密度（ρ）及其拉普拉斯值（∇2ρ）是判断相互作用类型和强度的关键指标。

### **表2：分子间键临界点（BCP）的QTAIM参数解读**

该表为用户提供了一个将QTAIM数值输出转化为化学语言的框架。

| 相互作用类型 | 典型的ρ (a.u.) | 典型的∇²ρ (a.u.) | 化学解释 |
| :---- | :---- | :---- | :---- |
| **共价键** | 较大 (\> 0.2) | 较大负值 | 共享壳层相互作用，电子在键区集中。 |
| **强氢键** | 中等 (0.02 \- 0.04) | 较小正值 | 部分共价特性的闭壳层相互作用。 |
| **弱氢键/范德华力** | 较小 (\< 0.02) | 较小正值 | 纯粹的闭壳层相互作用，电子在键区耗散。 |
| **离子键** | 极小 (\< 0.01) | 较大正值 | 极端的闭壳层相互作用，电荷分离。 |

### **4.4 使用MESP（分子静电势）绘制反应性图谱**

MESP可以直观地展示分子周围的电荷分布，揭示富电子（亲核）和缺电子（亲电）区域，从而解释分子间为何会以特定的方向相互靠近 29。

Multiwfn中的操作命令 32：

1. 启动Multiwfn，加载complex\_cp.fchk文件。  
2. 在主菜单中输入 12，选择“定量分子表面分析”。  
3. 输入 0，使用默认设置开始计算（将ESP投影到$\\rho=0.001$ a.u.的电子密度等值面上）。  
4. 根据提示导出可视化文件，例如选择 6 将所有表面顶点导出为.pdb文件。

结果解读：  
MESP图通常使用颜色编码：红色区域表示负静电势（富电子，如氢键受体位点），蓝色区域表示正静电势（缺电子，如氢键给体位点） 34。对于苯-甲烷复合物，苯环的π电子云区域呈现负静电势（红色），而甲烷的氢原子则带有轻微的正静电势（蓝色），这种静电势的互补性是驱动π-堆积相互作用的重要因素之一。

## **第五节：重要背景与局限性**

### **气相近似及其影响**

必须明确指出，本指南描述的整个工作流程计算的是两个分子在**真空**中的相互作用能。然而，许多现实世界的化学过程，如共晶的形成，发生在固相或溶液中 36。在晶格中，周期性的长程相互作用以及溶剂分子的存在，都可能显著改变分子间的相互作用能和几何构型。

因此，这里计算得到的气相$\\Delta E\_{int}$衡量的是分子间**内在**的相互作用强度。这是一个至关重要的基础信息，但对于预测凝聚相中的稳定性而言，它并非最终答案。对于精确的晶格能计算，需要采用更高级的理论方法，如周期性DFT计算 2。本教程所介绍的方法应被视为更复杂的多尺度模拟研究中的基础第一步。

### **工作流程的普适性**

尽管本教程以一个简单的二聚体为例，但其 underlying principles 是普适的，适用于任何非共价键合的超分子体系。Gaussian中的Counterpoise=N方法可以扩展到包含三个或更多片段的体系（N\>2）。同样，Multiwfn提供的分析工具，如NCI、QTAIM和MESP，也广泛适用于从主客体化学到生物大分子片段等各种复杂体系的研究。

## **结论**

本报告系统地介绍了一套结合Gaussian和Multiwfn的协同工作流程，用于计算和分析分子间的相互作用。该流程强调了理论与实践的结合：

* **定量严谨性**：通过Gaussian的超分子方法和Counterpoise校正，可以准确地计算出消除了BSSE赝象的相互作用能（）。  
* **定性洞察力**：通过Multiwfn的NCI、QTAIM和MESP分析，可以从电子结构层面深入揭示相互作用的类型、强度和物理本质。

遵循本指南的步骤，研究者不仅能得到一个可靠的能量数值，更能获得对分子间相互作用力的深刻化学理解，从而为材料设计、药物开发和基础化学研究提供坚实的理论支持。

#### **引用的著作**

1. Intermolecular Energies Calculated for 15 Coformers Possessing −COOH or... \- ResearchGate, 访问时间为 十月 11, 2025， [https://www.researchgate.net/figure/Intermolecular-Energies-Calculated-for-15-Coformers-Possessing-COOH-or-SO-3-H-Groups\_tbl2\_349654316](https://www.researchgate.net/figure/Intermolecular-Energies-Calculated-for-15-Coformers-Possessing-COOH-or-SO-3-H-Groups_tbl2_349654316)  
2. Prioritizing Computational Cocrystal Prediction Methods for ..., 访问时间为 十月 11, 2025， [https://pmc.ncbi.nlm.nih.gov/articles/PMC11594024/](https://pmc.ncbi.nlm.nih.gov/articles/PMC11594024/)  
3. Evaluating the Energetic Driving Force for Cocrystal Formation \- PMC, 访问时间为 十月 11, 2025， [https://pmc.ncbi.nlm.nih.gov/articles/PMC5806084/](https://pmc.ncbi.nlm.nih.gov/articles/PMC5806084/)  
4. 使用Multiwfn的定量分子表面分析功能预测反应位点、分析分子间相互 ..., 访问时间为 十月 11, 2025， [http://sobereva.com/159](http://sobereva.com/159)  
5. The Basis Set Superposition Error (BSSE) \- Prof. Hendrik Zipse, 访问时间为 十月 11, 2025， [https://zipse.cup.uni-muenchen.de/teaching/computational-chemistry-2/topics/the-basis-set-superposition-error-bsse/](https://zipse.cup.uni-muenchen.de/teaching/computational-chemistry-2/topics/the-basis-set-superposition-error-bsse/)  
6. 7.8 Basis Set Superposition Error (BSSE) \- Q-Chem Manual, 访问时间为 十月 11, 2025， [https://manual.q-chem.com/5.0/sect0022.html](https://manual.q-chem.com/5.0/sect0022.html)  
7. Counterpoise Correction and Basis Set Superposition Error, 访问时间为 十月 11, 2025， [https://vergil.chemistry.gatech.edu/notes/cp.pdf](https://vergil.chemistry.gatech.edu/notes/cp.pdf)  
8. Basis set superposition error \- Wikipedia, 访问时间为 十月 11, 2025， [https://en.wikipedia.org/wiki/Basis\_set\_superposition\_error](https://en.wikipedia.org/wiki/Basis_set_superposition_error)  
9. Distinguishing Basis Set Superposition Error (BSSE) from Basis Set Incompleteness Error (BSIE) \- Georgia Institute of Technology, 访问时间为 十月 11, 2025， [https://vergil.chemistry.gatech.edu/static/content/bsse-vs-bsie.pdf](https://vergil.chemistry.gatech.edu/static/content/bsse-vs-bsie.pdf)  
10. What is counterpoise correction? \- Computational Science Stack Exchange, 访问时间为 十月 11, 2025， [https://scicomp.stackexchange.com/questions/3/what-is-counterpoise-correction](https://scicomp.stackexchange.com/questions/3/what-is-counterpoise-correction)  
11. Behavior of counterpoise correction in many‐body molecular clusters of organic compounds: Hartree–Fock interaction energy perspective, 访问时间为 十月 11, 2025， [https://pmc.ncbi.nlm.nih.gov/articles/PMC9303541/](https://pmc.ncbi.nlm.nih.gov/articles/PMC9303541/)  
12. 2.11. Counterpoise Corrections \- ORCA 6.1 Manual, 访问时间为 十月 11, 2025， [https://orca-manual.mpi-muelheim.mpg.de/contents/essentialelements/counterpoise.html](https://orca-manual.mpi-muelheim.mpg.de/contents/essentialelements/counterpoise.html)  
13. Density-functional approaches to noncovalent interactions: A comparison of dispersion corrections (DFT-D), exchange-hole dipole \- Georgia Institute of Technology, 访问时间为 十月 11, 2025， [https://repository.gatech.edu/server/api/core/bitstreams/970427d2-5392-4b3d-8efe-d5df9c3c7046/content](https://repository.gatech.edu/server/api/core/bitstreams/970427d2-5392-4b3d-8efe-d5df9c3c7046/content)  
14. DFT-D and basis-set superposition error \- QuantumATK, 访问时间为 十月 11, 2025， [https://docs.quantumatk.com/tutorials/dispersion\_corrections\_and\_bsse/dispersion\_corrections\_and\_bsse.html](https://docs.quantumatk.com/tutorials/dispersion_corrections_and_bsse/dispersion_corrections_and_bsse.html)  
15. Density-functional approaches to noncovalent interactions: a comparison of dispersion corrections (DFT-D), exchange-hole dipole moment (XDM) theory, and specialized functionals \- PubMed, 访问时间为 十月 11, 2025， [https://pubmed.ncbi.nlm.nih.gov/21361527/](https://pubmed.ncbi.nlm.nih.gov/21361527/)  
16. A Comparison of the Behavior of Functional/Basis Set Combinations ..., 访问时间为 十月 11, 2025， [https://pmc.ncbi.nlm.nih.gov/articles/PMC3073166/](https://pmc.ncbi.nlm.nih.gov/articles/PMC3073166/)  
17. Comment on “Benchmarking Basis Sets for Density Functional Theory Thermochemistry Calculations: Why Unpolarized Basis Sets and the Polarized 6-311G Family Should Be Avoided” | The Journal of Physical Chemistry A \- ACS Publications, 访问时间为 十月 11, 2025， [https://pubs.acs.org/doi/10.1021/acs.jpca.4c00283](https://pubs.acs.org/doi/10.1021/acs.jpca.4c00283)  
18. Efficient Diffuse Basis Sets for Density Functional Theory \- ACS Publications, 访问时间为 十月 11, 2025， [https://pubs.acs.org/doi/10.1021/ct900566x](https://pubs.acs.org/doi/10.1021/ct900566x)  
19. Which Basis Set and Functional to use when? : r/comp\_chem \- Reddit, 访问时间为 十月 11, 2025， [https://www.reddit.com/r/comp\_chem/comments/107yl75/which\_basis\_set\_and\_functional\_to\_use\_when/](https://www.reddit.com/r/comp_chem/comments/107yl75/which_basis_set_and_functional_to_use_when/)  
20. Counterpoise | Gaussian.com, 访问时间为 十月 11, 2025， [https://gaussian.com/counterpoise/](https://gaussian.com/counterpoise/)  
21. G09 Keyword: Counterpoise, 访问时间为 十月 11, 2025， [https://wild.life.nctu.edu.tw/\~jsyu/compchem/g09/g09ur/k\_counterpoise.htm](https://wild.life.nctu.edu.tw/~jsyu/compchem/g09/g09ur/k_counterpoise.htm)  
22. Basis Set Superposition Error (BSSE). A short intro \- Dr. Joaquin Barroso's Blog, 访问时间为 十月 11, 2025， [https://joaquinbarroso.com/2020/12/08/basis-set-superposition-error-bsse-a-short-intro/](https://joaquinbarroso.com/2020/12/08/basis-set-superposition-error-bsse-a-short-intro/)  
23. Plotting NCI and AIM with Multiwfn and VMD | Home \- Sofia Kiriakidi, 访问时间为 十月 11, 2025， [https://sofki.github.io/2024-03-14-multiwfn/](https://sofki.github.io/2024-03-14-multiwfn/)  
24. Gallery, 访问时间为 十月 11, 2025， [http://sobereva.com/multiwfn/gallery\_2.html](http://sobereva.com/multiwfn/gallery_2.html)  
25. Live NCI Analysis For Periodic System Using Multiwfn software ||Part-2 Materials \- YouTube, 访问时间为 十月 11, 2025， [https://www.youtube.com/watch?v=IiE2h5Oqer4](https://www.youtube.com/watch?v=IiE2h5Oqer4)  
26. Live NCI Analysis From Scratch Using Gaussian and Multiwfn software \#NCIPlots ||Part-1-Molecules \- YouTube, 访问时间为 十月 11, 2025， [https://www.youtube.com/watch?v=VcrtLaT2lvc](https://www.youtube.com/watch?v=VcrtLaT2lvc)  
27. Performing Live QTAIM Analysis in Multiwfn | Understanding Bond Critical Points (BCPs), 访问时间为 十月 11, 2025， [https://www.youtube.com/watch?v=tnjPJrQxUCQ](https://www.youtube.com/watch?v=tnjPJrQxUCQ)  
28. QTAIM analysis / Multiwfn and wavefunction analysis / Multiwfn forum, 访问时间为 十月 11, 2025， [http://sobereva.com/wfnbbs/viewtopic.php?id=248](http://sobereva.com/wfnbbs/viewtopic.php?id=248)  
29. Molecular electrostatic potential analysis of non-covalent complexes, 访问时间为 十月 11, 2025， [https://www.ias.ac.in/public/Volumes/jcsc/128/10/1677-1686.pdf](https://www.ias.ac.in/public/Volumes/jcsc/128/10/1677-1686.pdf)  
30. Molecular electrostatic potential analysis: A powerful tool to interpret and predict chemical reactivity \- ResearchGate, 访问时间为 十月 11, 2025， [https://www.researchgate.net/publication/358433233\_Molecular\_electrostatic\_potential\_analysis\_A\_powerful\_tool\_to\_interpret\_and\_predict\_chemical\_reactivity](https://www.researchgate.net/publication/358433233_Molecular_electrostatic_potential_analysis_A_powerful_tool_to_interpret_and_predict_chemical_reactivity)  
31. A Molecular Electrostatic Potential Analysis of Hydrogen, Halogen ..., 访问时间为 十月 11, 2025， [https://www.researchgate.net/publication/260128408\_A\_Molecular\_Electrostatic\_Potential\_Analysis\_of\_Hydrogen\_Halogen\_and\_Dihydrogen\_Bonds](https://www.researchgate.net/publication/260128408_A_Molecular_Electrostatic_Potential_Analysis_of_Hydrogen_Halogen_and_Dihydrogen_Bonds)  
32. Plotting electrostatic potential colored molecular surface map with ESP surface extrema via Multiwfn and VMD, 访问时间为 十月 11, 2025， [http://sobereva.com/multiwfn/res/plotESPsurf.pdf](http://sobereva.com/multiwfn/res/plotESPsurf.pdf)  
33. Using Multiwfn and VMD to easily plot electrostatic potential colored molecular vdW surface map \- YouTube, 访问时间为 十月 11, 2025， [https://www.youtube.com/watch?v=QFpDf\_GimA0](https://www.youtube.com/watch?v=QFpDf_GimA0)  
34. Molecular electrostatic potential dependent selectivity of hydrogen bonding \- ResearchGate, 访问时间为 十月 11, 2025， [https://www.researchgate.net/publication/266326307\_Molecular\_electrostatic\_potential\_dependent\_selectivity\_of\_hydrogen\_bonding](https://www.researchgate.net/publication/266326307_Molecular_electrostatic_potential_dependent_selectivity_of_hydrogen_bonding)  
35. Electrostatic Potential Maps and Bond Polarity \- Organic Chemistry \- YouTube, 访问时间为 十月 11, 2025， [https://www.youtube.com/watch?v=Sd\_2RwNE4iU](https://www.youtube.com/watch?v=Sd_2RwNE4iU)  
36. Periodic DFT Calculations—Review of Applications in the Pharmaceutical Sciences \- PMC, 访问时间为 十月 11, 2025， [https://pmc.ncbi.nlm.nih.gov/articles/PMC7284980/](https://pmc.ncbi.nlm.nih.gov/articles/PMC7284980/)  
37. Inaccurate Conformational Energies Still Hinder Crystal Structure Prediction in Flexible Organic Molecules \- ACS Publications, 访问时间为 十月 11, 2025， [https://pubs.acs.org/doi/10.1021/acs.cgd.0c00676](https://pubs.acs.org/doi/10.1021/acs.cgd.0c00676)  
38. Frontiers of molecular crystal structure prediction for pharmaceuticals and functional organic materials \- PubMed Central, 访问时间为 十月 11, 2025， [https://pmc.ncbi.nlm.nih.gov/articles/PMC10685338/](https://pmc.ncbi.nlm.nih.gov/articles/PMC10685338/)