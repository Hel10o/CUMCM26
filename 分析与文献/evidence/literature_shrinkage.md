# 第4问：收缩、移动边界与水热传递文献核验

检索日期：2026-09-10。依据本项目 `problem_text.txt` 中第4问及附录4。仅检索已发表学术文献；不含当年题解、参赛者讨论或论坛材料。本文是建模前的文献证据与方程审查，不是已完成的数值结果。

## 1. 高匹配文献（建议阅读顺序）

### S1. 圆柱、变物性、收缩和全隐式有限体积

**Wilton Pereira da Silva, Cleide M.D.P.S. e Silva, Fernando J.A. Gama.** Estimation of thermo-physical properties of products with cylindrical shape during drying: The coupling between mass and heat. **Journal of Food Engineering**, 2014, **141**: 65–73. DOI: **10.1016/j.jfoodeng.2014.05.010**。

- 原始出版页：[ScienceDirect](https://www.sciencedirect.com/science/article/pii/S0260877414002118)；[DOI](https://doi.org/10.1016/j.jfoodeng.2014.05.010)。
- 已核验范围：出版社网页的检索索引返回题名、作者、期刊卷页、DOI、Highlights 和摘要；直接打开网页返回403。**未获取全文，未逐式核验离散系数。**
- 已核验方法：一维圆柱扩散模型，第三类（对流）边界条件；考虑变热物性与收缩；全隐式有限体积离散；表面热质耦合。论文应用对象为整根香蕉。
- 题问映射：第2—4问的数值结构最接近，尤其适合第4问采用圆环控制体和变半径网格的实现参考。
- 使用边界：可作为方法选型依据；不能在未读全文时声称其收缩速度、守恒变量或离散公式与本题一致；不能移植香蕉的参数。

### S2. 非等温移动边界：水分输运、热传递和 ALE

**Alessandra Adrover, Claudia Venditti, Antonio Brasiello.** A Non-Isothermal Moving-Boundary Model for Continuous and Intermittent Drying of Pears. **Foods**, 2020, **9**(11): 1577. DOI: **10.3390/foods9111577**。

- [原始论文开放全文（PMC）](https://pmc.ncbi.nlm.nih.gov/articles/PMC7692062/)；[DOI](https://doi.org/10.3390/foods9111577)。
- 已核验范围：全文网页的摘要、第3节方程(1)—(13)和数值方法段；正文明确使用 FEM 与 ALE 动网格。
- 已核验方法：通过局部收缩速度描述移动边界；联立水分与能量的平流扩散方程；表面条件包含传热与蒸发耗热；扩散系数依赖局部温度。
- 题问映射：第2—4问水热耦合及第4问移动边界的理论参考。正文的体积水浓度有质量/体积单位，**不能直接等同题目中的干基含水率 $C$**。
- 使用边界：该文以梨和自身的收缩本构预测边界；本题附件2已经给出半径，应先用其驱动几何，避免同时强制另一套收缩本构。表面潜热、解吸等温线是扩展模型，是否引入要结合本题给定信息，不能用未辨识参数替换题定经验式。

### S3. 移动边界收缩框架的原始论文

**A. Adrover, A. Brasiello, G. Ponso.** A moving boundary model for food isothermal drying and shrinkage: General setting. **Journal of Food Engineering**, 2019, **244**: 178–191. DOI: **10.1016/j.jfoodeng.2018.09.018**。

- [原始出版页](https://www.sciencedirect.com/science/article/abs/pii/S0260877418304060)；[DOI](https://doi.org/10.1016/j.jfoodeng.2018.09.018)。
- 已核验范围：出版社检索索引中的完整摘要、Highlights、部分方法与结论预览；直接打开网页返回403。**未取得全文。**
- 已核验方法：将局部收缩速度与水扩散通量关联，比例因子可依赖局部含水体积分数；允许样品体积损失小于、等于或大于排出水的体积；适用于圆柱等多种几何形状。
- 题问映射：第4问为何需要“材料速度—网格运动—传质”相容模型，以及为什么不能把“体积减少=失水体积”当作无需证明的事实。
- 使用边界：本文为等温框架；不能直接覆盖第2问预热阶段。题目只有 $R(t)$ 时，不能声称已识别全文的局部收缩因子。

### S4. 实验收缩输入、非各向同性和 ALE

**Poonam Rani, P. P. Tripathy.** Modelling of moisture migration during convective drying of pineapple slice considering non-isotropic shrinkage and variable transport properties. **Journal of Food Science and Technology**, 2020, **57**: 3748–3761. DOI: **10.1007/s13197-020-04407-4**。

- [原始出版页（Springer）](https://link.springer.com/article/10.1007/s13197-020-04407-4)；[PMC全文入口](https://pmc.ncbi.nlm.nih.gov/articles/PMC7447739/)；[DOI](https://doi.org/10.1007/s13197-020-04407-4)。
- 已核验范围：Springer题录、摘要及术语表；PMC检索索引给出方法与结论段，但本次直接打开触发验证码。**尚未逐式精读全文。**
- 已核验方法：三维有限元；含水率相关扩散系数和传质系数；分方向收缩；利用 ALE 方法容纳几何变化；与实验平均含水率验证。
- 题问映射：第4问几何变化处理，以及“测得半径收缩”不自动推出“轴向同倍率收缩”。本题长细圆柱仍可先做一维径向模型。
- 使用边界：菠萝环是空心且近薄片的几何，不能照搬成一维长实心圆柱；论文的拟合误差和收缩幅度只对其实验有效。

### S5. 为什么收缩维数和坐标定义影响方程

**Pascual E. Viollaz, Clara O. Rovedo.** A drying model for three-dimensional shrinking bodies. **Journal of Food Engineering**, 2002, **52**(2): 149–153. DOI: **10.1016/S0260-8774(01)00097-8**。

- [原始出版页](https://www.sciencedirect.com/science/article/abs/pii/S0260877401000978)；[DOI](https://doi.org/10.1016/S0260-8774(01)00097-8)。
- 已核验范围：出版社检索索引中的题录、摘要和质量守恒方程预览；直接打开网页返回403。**未取得全文。**
- 已核验方法：在单向干燥、三维收缩条件下，对有限平板建立质量输运方程；用有限差分求解；指出非单向收缩会引入质量平衡中的对流贡献。
- 题问映射：第4问坐标与收缩假设的审查来源。
- 使用边界：文中为平板且用第一类边界，不能当作本题圆柱Robin边界的直接求解模板；不能从这篇论文推出“所有收缩模型都必须显式多一个对流项”。

## 2. 第4问必须先说明的变量与守恒关系

以下是针对本题的推导与审查建议，**不是从上述论文直接照抄的方程**。

令 $C$ 为干基含水率，$\rho_d$ 为“单位当前体积中的干物质量”，$u$ 为固体骨架的径向速度；先假设轴向长度不变、径向对称、干物质不流失。$C$ 是 kg水/kg干物质，不能当作 kg水/m³。取相对固体骨架的水通量

$$
j=-\rho_d D\frac{\partial C}{\partial r}
\qquad \left[\frac{\mathrm{kg}}{\mathrm{m}^2\cdot\mathrm{s}}\right]
$$

则干物质守恒与水分守恒分别为

$$
\begin{aligned}
\frac{\partial\rho_d}{\partial t}
+\frac{1}{r}\frac{\partial(r\rho_d u)}{\partial r}&=0,\\
\frac{\partial(\rho_d C)}{\partial t}
+\frac{1}{r}\frac{\partial\left[r(\rho_d C u+j)\right]}{\partial r}&=0.
\end{aligned}
$$

相减得到干基含水率的输运方程

$$
\rho_d\left(\frac{\partial C}{\partial t}+u\frac{\partial C}{\partial r}\right)
=\frac{1}{r}\frac{\partial}{\partial r}
\left(r\rho_d D\frac{\partial C}{\partial r}\right)
$$

这里的通量本构是一项明确假设；它与题目常见的表观含水率扩散模型之间，需要在 $\rho_d$ 的选取和空间均匀性上说明简化。若用单位体积水浓度 $w=\rho_d C$ 作未知量，压缩引起的体积浓度变化会出现在守恒式中；不能把 $w$ 的压缩项直接搬给 $C$。

若题给 $\rho(C)$ 被解释为当前湿物料的体积密度，则 $\rho_d=\rho/(1+C)$。但同时指定 $\rho(C)$、实测 $R(t)$ 和内部均匀收缩速度，未必保证干物质总量不变。必须检查相容性；不要把题目的经验热物性式无说明地提升为精确收缩本构。

## 3. “把 $R$ 改成 $R(t)$”是否漏项，取决于坐标和材料速度

设 $\xi=r/R(t)$，$q(\xi,t)=C(r,t)$，网格径向速度 $v_g=\xi R'(t)$。前述方程变为

$$
\frac{\partial q}{\partial t}
+\frac{u-\xi R'(t)}{R(t)}\frac{\partial q}{\partial\xi}
=\frac{1}{\rho_d R(t)^2\xi}\frac{\partial}{\partial\xi}
\left(\xi\rho_d D\frac{\partial q}{\partial\xi}\right)
$$

因此有两种需要区分的情形：

1. **均匀径向收缩、网格跟随材料**：$u=rR'/R=\xi R'$，相对速度为零，显式对流项抵消。若 $\rho_d$ 空间均匀，右端也可约去 $\rho_d$，得到含 $1/R(t)^2$ 的扩散算子。此时没有单独写对流项可以是正确的，前提是材料坐标和干物质守恒假设清楚。
2. **在空间坐标中先写 $C_t=(1/r)(rDC_r)_r$，再把变化区域映射为固定 $\xi$ 区间**：链式法则给出 $q_t=R^{-2}\xi^{-1}(\xi Dq_\xi)_\xi+\xi(R'/R)q_\xi$。漏掉该映射项会改变原来的空间方程。该简化空间模型本身是否描述真实收缩材料，还需另作物理判断。

必须避免在软件 ALE 已处理相对网格速度后，手动再加一次同一对流项。只有附件中的表面 $R(t)$，不能唯一确定内部 $u(r,t)$；均匀收缩需要作为假设。若假设长度不变且均匀径向收缩，$\rho_d$ 应随 $R^{-2}$ 变化以保持干物质量。

建议使用的整体核验是

$$
\begin{aligned}
M_d&=2\pi L\int_0^{R(t)}\rho_d(r,t)\,r\,\mathrm{d}r
&&\text{应保持不变},\\
M_w&=2\pi L\int_0^{R(t)}\rho_d(r,t)C(r,t)\,r\,\mathrm{d}r,\\
\frac{\mathrm{d}M_w}{\mathrm{d}t}&=-2\pi R(t)Lj(R(t),t)
&&\text{无端面通量时}.
\end{aligned}
$$

若选用题定简化表观扩散模型而没有引入 $\rho_d$，必须如实说明检验的是离散方程的守恒，不应自动声称实现了完整物理质量守恒。

## 4. 第3问与第4问的烘干时差不是纯收缩效应

附录3到附录4同时更换 $\rho$、$c_p$、$k$、$D$。故 $t_4-t_3$ 同时包含几何与物性变化，不能全部归因收缩。

最少应增加一个诊断算例：**采用附录4的全部物性，固定 $R=R_0$**。将其与“附录4物性+实测 $R(t)$”对比，才能在相同物性下讨论给定半径变化对时长的影响。若希望分解相互作用，可做“附录3/4物性 × 固定/变化半径”的四种计算；此为模型内消融比较，不是独立实验的因果验证。

## 5. 半径插值、输出和结束条件

- $R$ 数据先统一为米和秒；检查正值、单调性、异常点及覆盖时段，再选分段线性或保形插值，避免无依据的高阶多项式外推。
- 内部计算网格可以固定为 $\xi\in[0,1]$；输出必须转换回题目指定的**实际到中心距离**。不能将 $\xi=0.5$ 当成恒定半径位置。
- 对每个时刻，只在 $0\le r\le R(t)$ 的材料内输出 $C$；题目要求的表面位置应单独计算。不得将已位于材料外的网格点填成0并用其参与终止判据。
- 烘干终止条件应为当前材料域上的最大含水率低于0.15。中心是否始终最湿需结合解的单调性验证；体积平均含水率达标不能替代“各处达标”。

## 6. 下一步精读建议

优先获取 S1 全文，核查圆柱有限体积的控制体、表面热质条件及收缩网格更新。S2 可直接阅读开放全文第3节，其最有价值之处是变量定义与守恒结构。S3—S5用于验证收缩与坐标处理的假设边界，不能替代本题给定经验式和实测半径数据。
