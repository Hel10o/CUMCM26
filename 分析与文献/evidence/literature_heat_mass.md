# 问题 1—3：热质传递与数值方法文献核验

检索日期：2026-09-10。已先读取本地题目文本；按圆柱径向扩散、变物性热质耦合、对流边界检索既有研究，没有检索当年题解。以下六篇为重点核验候选，前五篇建议保留，第六篇作为更复杂模型的补充。书目信息和方法依据均来自出版社原始页面或作者所在大学的机构库；搜索结果中的第三方聚合站未作为证据。

这里的“已读”分别标为“摘要”“摘要及正文节选”“全文页面的方法和验证部分”；不能理解为所有论文已下载并通读。部分出版社网页直接打开受限，但其可检索的原始页面提供了摘要和正文节选。

## 一、优先保留的五篇

### H1：一维圆柱、第三类边界和完全隐式有限体积，匹配度最高

**Wilton Pereira da Silva, Cleide M.D.P.S. e Silva, Fernando J.A. Gama.** Estimation of thermo-physical properties of products with cylindrical shape during drying: The coupling between mass and heat. **Journal of Food Engineering, 2014, 141: 65–73.** DOI：[10.1016/j.jfoodeng.2014.05.010](https://doi.org/10.1016/j.jfoodeng.2014.05.010)。[出版社原始页面](https://www.sciencedirect.com/science/article/pii/S0260877414002118)。

- 阅读证据：已读出版社摘要和 Highlights；未通读全文。
- 方法核验：一维圆柱坐标下的表观液态水扩散；第三类对流边界；完全隐式有限体积离散；模型包含变物性与收缩，并用优化反演物性参数。对象为整根香蕉。
- 对应题问：问题 1 的径向网格与对流边界；问题 2—3 的变系数长期积分；问题 4 可进一步核验收缩实现。
- 可借鉴：用圆柱控制体积组织通量及边界交换、采用隐式推进的求解骨架。
- 不能直接搬用：香蕉材料参数、反演结果和收缩律；本题已给经验式和附件，通常无须重新反演参数。仅凭摘要尚不能确认其非线性迭代细节或具体停止误差。

### H2：局部温湿度决定物性，适合作为问题 2 的模型依据

**Maria Aversa, Stefano Curcio, Vincenza Calabrò, Gabriele Iorio.** An analysis of the transport phenomena occurring during food drying process. **Journal of Food Engineering, 2007, 78(3): 922–932.** DOI：[10.1016/j.jfoodeng.2005.12.005](https://doi.org/10.1016/j.jfoodeng.2005.12.005)。[出版社原始页面](https://www.sciencedirect.com/science/article/abs/pii/S026087740500796X)。

- 阅读证据：已读出版社摘要；有作者博士论文机构库入口，但本次未成功读取对应全文，故不标为全文已读。
- 方法核验：同时求解二维非稳态热量与水分 PDE，空气和食品物性随局部温度、含水率变化；用 FEMLAB 有限元求解。模型考虑食品内部水分迁移及界面蒸发/凝结。
- 对应题问：问题 2—3，尤其是题给 $\rho(C)$、$c_p(C)$、$k(C)$、$D(T,C)$ 的耦合结构。
- 可借鉴：局部更新物性、区分内传递与界面交换，以及用实验比较模型预测的验证逻辑。
- 不能直接搬用：二维几何、材料物性及界面关联式；论文未纳入收缩，对后期偏差有明确讨论，不能据此声称已解决问题 4。
- 书目注意：期刊年为 2007，DOI 中含 2005 并不矛盾；个别作者履历中的 DOI 排列存在串位，以上采用出版社记录。

### H3：可读取方法公式的 $D(T,X)$ 与对流边界实例

**Prarin Chupawa, Wanwisa Suksamran, Donludee Jaisut, Frederik Ronsse, Wasan Duangkhamchan.** Combined Heat and Mass Transfer Associated with Kinetics Models for Analyzing Convective Stepwise Drying of Carrot Cubes. **Foods, 2022, 11(24): 4045.** DOI：[10.3390/foods11244045](https://doi.org/10.3390/foods11244045)。[出版社全文页面](https://www.mdpi.com/2304-8158/11/24/4045)，[根特大学机构库及 PDF 下载入口](https://biblio.ugent.be/publication/01GPBC1BFWBZA89092X24SCDE3)。

- 阅读证据：已读出版社全文页面中的 §2.1 方法及 §3.1 验证、讨论部分；元数据另以根特大学作者库交叉核验。
- 方法核验：有限元联立导热与 Fick 扩散；式 (3) 采用 $\partial X/\partial t=\nabla\cdot(D_{\mathrm{eff}}\nabla X)$，式 (4) 中 $D_{\mathrm{eff}}$ 同时依赖温度与干基含水率；式 (5)—(6) 为表面对流交换，并在热边界考虑水分通量对应的能量项。
- 对应题问：问题 1—3 的 PDE、变系数处理及中心/表面非均匀分布；变温工况可供解释附件 1 的使用方式。
- 可借鉴：系数应放在散度内部；用局部场解释外干内湿；将模型结果与独立实验量比较。
- 不能直接搬用：立方体坐标、胡萝卜经验系数和阶段切换阈值。§3.1.1 明确说明其经验收缩方程没有反馈到热质 PDE，因此该文不是问题 4 动边界模型的直接依据。引用热边界前还需自行检查法向、通量符号及单位。

### H4：圆柱薄片有限体积热质耦合，注意一维方向不等于本题径向

**Dimitrios A. Tzempelikos, Dimitris Mitrakos, Alexandros P. Vouros, Achilleas V. Bardakas, Andronikos E. Filios, Dionissios P. Margaris.** Numerical modeling of heat and mass transfer during convective drying of cylindrical quince slices. **Journal of Food Engineering, 2015, 156: 10–21.** DOI：[10.1016/j.jfoodeng.2015.01.017](https://doi.org/10.1016/j.jfoodeng.2015.01.017)。[出版社原始页面](https://www.sciencedirect.com/science/article/pii/S0260877415000357)。

- 阅读证据：已读出版社摘要、建模引言和结论节选；未通读全文。
- 方法核验：一维导热与水分扩散方程用有限体积求解，采用第三类 Robin 边界处理蒸发项；扩散系数含 Arrhenius 温度依赖。外部 SST-k-omega CFD 求换热系数，再由热质传递类比求传质系数。
- 对应题问：问题 1—3 的热质耦合与边界组织；可作为 H1 的补充。
- 可借鉴：区分内部扩散与界面蒸发；热湿物性变化；对不同工况做预测验证。
- 不能直接搬用：这是迎风圆柱薄片，不能仅凭题名把其一维方向当成长圆柱径向；本题已给换热和传质系数，无须为此建立外部湍流 CFD。榅桲材料系数、流动关联式不可替代题给参数。

### H5：真实药用根部的径向内外传质阻力证据

**A. I. Martynenko.** Evaluation of Mass Transfer Resistances from Drying Experiments. **Drying Technology, 2006, 24(12): 1569–1582.** DOI：[10.1080/07373930601030838](https://doi.org/10.1080/07373930601030838)。[出版社原始页面](https://www.tandfonline.com/doi/full/10.1080/07373930601030838)。

- 阅读证据：已读出版社摘要；未取得可确认的完整正文。
- 方法核验：对人参根建立一维径向复合传质阻力模型；把芯部、表皮扩散阻力与空气边界层阻力组合，通过改变风速和是否去皮的实验分离各项阻力，并检查阻力与干燥速率因子的关系。
- 对应题问：问题 1—3 的传质边界与内部扩散是否均需保留；作为药材背景依据。
- 可借鉴：不能未经检验就把表面浓度直接设为环境浓度；药材表皮和外部空气边界层可形成实质阻力。
- 不能直接搬用：该文是阻力识别研究，不提供本题完整的温度场数值求解器；不能拿人参测得系数替代题中经验公式，也不能由整体速率拟合推定“各处均低于阈值”。
- 年份注意：卷期标为 2006，网页在线发布日期为 2007-04-18。参考文献按卷期年写 2006。

## 二、降低优先级的第六篇

**Stefano Curcio, Maria Aversa, Vincenza Calabrò, Gabriele Iorio.** Simulation of food drying: FEM analysis and experimental validation. **Journal of Food Engineering, 2008, 87(4): 541–553.** DOI：[10.1016/j.jfoodeng.2008.01.016](https://doi.org/10.1016/j.jfoodeng.2008.01.016)。[出版社原始页面](https://www.sciencedirect.com/science/article/pii/S0260877408000381)。

已读摘要和引言节选。有限元同时求空气动量、固体与空气的热质传递，以界面通量连续避免预设界面传递系数，应用对象包含圆柱形蔬菜。与本题有物理联系，但本题给定烘房工况和表面传递系数，构建整烘房流场会引入大量未知几何和流动条件。因此作为理解复杂模型的补充，不作为首选实现路线。

## 三、对本题分析的直接启示

以下是根据题目与以上来源作出的建模判断，不是论文中针对本题给出的结论。

1. 问题 1—3 要输出径向局部场，单一 Page/Midilli 等平均含水率经验曲线不够。可先论证长圆柱的一维径向近似，保留中心对称边界与表面对流边界；长度 25 cm、半径 2 cm 并不能自动证明所有端部效应都可忽略。
2. 问题 2 给变系数后，扩散算子应从通量守恒推导。$\nabla\cdot(D\nabla C)$ 一般不等于 $D\nabla^2 C$；导热系数也同理。圆柱有限体积在轴心没有显式 $1/r$ 除零，因而是值得优先采用的实现路线。
3. 文献常包含蒸发潜热或湿空气—固体平衡关系。题目并未给齐相关参数，基础模型如仅采用题给传递系数和经验式，应明确简化范围；不能未说明就把别种材料的蒸发/吸附公式塞入模型。
4. 药材干基含水率与空气湿度虽然都可写 kg/kg，分母物理意义未必相同。若按题意直接写线性浓度差对流边界，应注明采用题目统一的等效浓度尺度；更细致的物理模型须补充平衡吸附或分配关系。
5. 问题 3 的终止量是 $\max_r C(r,t)$，不是空间平均含水率。中心通常最湿的说法需要从本题解和边界条件检查，不能只据其他材料的图直接代替检查。
6. 文献的实验吻合不等于本题模型已经验证。本题后续计算仍需检查水分通量平衡、非负性、网格/时间步收敛、对流边界残差，以及系数温度使用 K 而不是 °C。

## 四、可复用检索式

- `cylindrical drying variable properties convective boundary finite volume fully implicit`
- `coupled heat mass transfer drying local temperature moisture dependent diffusivity FEM`
- `ginseng root radial drying diffusive convective resistance`
- `cylindrical quince drying Robin boundary finite volume`
