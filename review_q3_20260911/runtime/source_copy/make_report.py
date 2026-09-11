"""Generate the paper-ready Q3 narrative and figures from actual verification JSON."""
from pathlib import Path
import json
import numpy as np

def table(rows,heads,fmts):
 s='| '+' | '.join(heads)+' |\n|'+ '|'.join(['---']*len(heads))+'|\n'
 for row in rows:s+='| '+' | '.join(format(v,fmt) if isinstance(v,(int,float)) else str(v) for v,fmt in zip(row,fmts))+' |\n'
 return s

def figures(p):
 import matplotlib
 matplotlib.use('Agg')
 import matplotlib.pyplot as plt
 a=np.load(p/'output/main.npz');tt=a['time_s']/3600;f=a['full_TC'];w=a['weights'].ravel();cc=f[:,:,:,1].reshape(len(tt),-1)
 avg=cc@w/w.sum();maximum=cc.max(axis=1)
 np.savez_compressed(p/'output/curves.npz',time_s=a['time_s'],center_C=cc[:,0],surface_C=cc[:,-1],maximum_C=maximum,volume_mean_C=avg)
 fig,ax=plt.subplots(figsize=(8,4.8));ax.plot(tt,cc[:,0],label='Axis');ax.plot(tt,cc[:,-1],label='Surface');ax.plot(tt,avg,label='Volume mean');ax.plot(tt,maximum,':',label='Full-mesh maximum');ax.axhline(.15,ls='--',label='Threshold 0.15');ax.set(xlabel='Time (h)',ylabel='Dry-basis moisture (kg/kg)',xlim=(0,58));ax.legend();ax.grid(True,alpha=.25);fig.tight_layout();fig.savefig(p/'output/moisture_history.png',dpi=180);plt.close(fig)
 sn=a['snapshot_time_s'];ss=a['snapshots'][:,:,0,:];r=a['r_m']*100
 fig,ax=plt.subplots(figsize=(8,4.8))
 for target in (21600,64800,129600,float(sn[-1])):
  i=int(np.argmin(abs(sn-target)));ax.plot(r,ss[i,:,1],label=f'{sn[i]/3600:.4f} h')
 ax.axhline(.15,ls='--',label='Threshold');ax.set(xlabel='Radius (cm)',ylabel='Dry-basis moisture (kg/kg)',xlim=(0,2));ax.legend();ax.grid(True,alpha=.25);fig.tight_layout();fig.savefig(p/'output/radial_profiles.png',dpi=180);plt.close(fig)
 from q3_solver import props
 D=props(ss[-1,:,0],ss[-1,:,1])[2]
 fig,ax=plt.subplots(figsize=(8,4.8));ax.semilogy(r,D);ax.set(xlabel='Radius (cm)',ylabel='Local diffusivity (m²/s)',title='Diffusivity at the strict execution endpoint');ax.grid(True,alpha=.25);fig.tight_layout();fig.savefig(p/'output/endpoint_diffusivity.png',dpi=180);plt.close(fig)
 if (p/'validation/cylinder80x64_iso.npz').exists():
  b=np.load(p/'validation/cylinder80x64_iso.npz');C=b['snapshots'][-1,:,:,1]
  fig,ax=plt.subplots(figsize=(8,4.8));im=ax.pcolormesh(b['z_m']*100,b['r_m']*100,C,shading='auto');fig.colorbar(im,ax=ax,label='Dry-basis moisture (kg/kg)');ax.set(xlabel='Distance from midplane (cm)',ylabel='Radius (cm)',title='Finite-cylinder check at its own endpoint (not Table 5)');fig.tight_layout();fig.savefig(p/'output/finite_cylinder_profile.png',dpi=180);plt.close(fig)

def generate(p):
 p=Path(p);s=json.loads((p/'validation/summary.json').read_text());e=s['event'];r=s['regression'];b=s['balance'];conv=s['convergence'];mech=s['mechanism'];xlsx=json.loads((p/'validation/xlsx_readback.json').read_text())
 t5=table(s['table5'],['时间/h','0 cm','0.5 cm','1 cm','1.5 cm','2 cm'],['.4f']*6)
 names={'integral512':'末1 h均值保持','scenario_last':'末值保持','scenario_nominal':'50℃、0.05保持','hT_minus20':'hT降低20%','hT_plus20':'hT增加20%','hm_minus20':'hm降低20%','hm_plus20':'hm增加20%'}
 scene=table([[names[x['case']],*x['future'],x['critical_h'],x['change_from_same_grid_baseline_s']/3600] for x in s['scenarios']],['情景','后续T/℃','后续C/(kg/kg)','临界时间/h','相对同网格基线变化/h'],['','.6f','.9f','.6f','+.6f'])
 grids=table([[x['case'],x['n'],x['critical_s'],x['critical_h']] for x in conv['events']],['算例','径向区间数','临界时间/s','临界时间/h'],['','.0f','.9f','.9f'])
 geo=table([[x['case'],x['critical_s'],x['end_effect_vs_matching_radial_s']] for x in s['geometry']],['有限圆柱算例','本算例临界时间/s','相对匹配径向网格变化/s'],['','.6f','+.6f'])
 refs='''[1] da Silva W. P. 等. Estimation of thermo-physical properties of products with cylindrical shape during drying: The coupling between mass and heat. Journal of Food Engineering, 141 (2014):65–73. DOI: 10.1016/j.jfoodeng.2014.05.010。本文使用PDF物理页3–5，§2.2–2.4，式(1)、(6)–(14)、(18)。

[2] Chupawa 等. Combined Heat and Mass Transfer Associated with Kinetics Models for Analyzing Convective Stepwise Drying of Carrot Cubes. Foods, 11(24),4045 (2022). DOI: 10.3390/foods11244045。本文使用PDF页3–6，式(3)–(6)、§3.1.1。

[3] Adrover A. 等. A Non-Isothermal Moving-Boundary Model for Continuous and Intermittent Drying of Pears. Foods, 9(11),1577 (2020). DOI: 10.3390/foods9111577。本文使用PDF页4–7，式(5)–(14)、§3.3。

[4] Maddix D. C., Sampaio L., Gerritsen M. Numerical Artifacts in the Generalized Porous Medium Equation: Why Harmonic Averaging Itself Is Not to Blame. Journal of Computational Physics,361 (2018):280–298. DOI:10.1016/j.jcp.2018.02.010。[作者v5原文](https://arxiv.org/pdf/1709.02581v5)。通过未带版本的作者PDF入口读取，首页核实为v5，13 Feb 2018，22页；使用页2式(1.3)，页5–6式(2.3)–(2.7)，页17–18 §5.2、图16–18。
'''
 text=rf'''# 第三问分析与最终答案

## 1　结论与适用口径

采用固定几何、轴向均匀的径向有效模型，并将4小时后的环境保持为末1小时观测均值，临界烘干时长为 **57.4740 h**。该数值是连续下穿的界限，不将等于0.15误写成严格达标；正式表5和Excel统一采用 **57.4741 h** 的执行结束行。

主模型的“全药材”指轴向均匀假设下的全部半径及全部轴向位置，不是仅检查21个输出点。端面忽略交换是明确的几何假设，另以长时二维轴对称模型检验其影响。二维结果用于辨别模型误差，没有与主模型的表格混写。

本轮从0秒重新积分，未把第二问的21个展示点或舍入值作为续算初态。未采用交接先导时间作为目标，也没有根据题目背景的“2—3天”调整物性、边界或终止条件；时长来自给定方程、输入观测与明示延拓的求解。

## 2　数据契约与未来环境

原题PDF第2页要求药材各处水分浓度低于0.15 kg/kg，第3页明确Excel的A列为秒、首行为半径厘米，第4页说明附录3同时适用于第二、三问。原件实际解析并核对页面，结果模板按事件动态扩展，未把省略号当作固定行数。

附件1为241条0—14400秒观测，间隔60秒。观测区间内对温度和环境水分浓度分别作分段线性插值，并在每个插值节点重启积分区间，避免跨越导数折点。4小时处仅切换环境函数，内部温度和水分场保持连续。

取10800—14400秒、含两端的61点作为平台统计窗口。主情景在4小时之后固定为下式；这是有依据的工作假设，不是后续实测。选择均值是为避免把一个尾点的波动固定数十小时，替代方案则通过实际事件时间比较。

$$T_\infty=49.99893442622951\ ^\circ\mathrm C,\qquad C_\infty=0.04998754098360656\ \mathrm{{kg/kg}}.$$

同窗口温度范围为49.757—50.236℃，水分浓度范围为0.04975—0.05024。末次观测为50.165℃、0.04986。附件没有提供4小时后的控制日志，故不存在脱离未来边界假设的唯一实测烘干时长。

## 3　模型建立

药材取半径R=0.02 m、长度L=0.25 m的固定圆柱，初始温度28℃、干基含水率2.55 kg/kg。第三问不使用附件2收缩数据或附录4物性。主域轴向均匀，端面不计交换；侧面与环境进行对流换热和等效传质。

令T为摄氏温度、T_K=T+273.15为绝对温度，C为每千克干物质所含水质量。由题给经验公式，设置局部物性而不是以空间平均值代替；温度容量、导热系数和扩散系数均在积分过程中随当前状态更新。

$$\rho(C)=650+128C,\quad c_p(C)=1450+2736\frac C{{1+C}},\quad k(C)=0.21+0.38\frac C{{1+C}},$$

$$S(C)=\rho(C)c_p(C),\qquad D(T_K,C)=2.4\times10^{{-3}}\exp(-0.45/C)\exp(-3850/T_K).$$

$$S(C)\frac{{\partial T}}{{\partial t}}=\frac1r\frac{{\partial}}{{\partial r}}\left(rk(C)\frac{{\partial T}}{{\partial r}}\right),\qquad \frac{{\partial C}}{{\partial t}}=\frac1r\frac{{\partial}}{{\partial r}}\left(rD(T_K,C)\frac{{\partial C}}{{\partial r}}\right).$$

中心采用对称零通量。侧面沿外法向写成下式，并继承附录2的h_T=25 W/(m²·K)、h_m=8×10⁻⁷ m/s，作为第三问未另给换热、传质系数时的明确假设。环境水分数值直接作为等效Robin边界量使用。

$$-k_sT_r(R,t)=h_T(T_s-T_\infty),\qquad -D_sC_r(R,t)=h_m(C_s-C_\infty),\qquad T_r(0,t)=C_r(0,t)=0.$$

这里的热储存项是S(C)T_t，不能擅自改成∂t(ST)，也不能将导热系数换成热扩散率后移入散度。水分平均及收支采用固定参考干密度的体积权重，不把随C变化的ρ同时解释成固定体积内严格守恒的真实混合密度。

气相湿度与固体平衡干基含水率并非因单位都写kg/kg就自然相同。本模型采用题目简化所需的等效映射。显式加入潜热、携焓、辐射或吸附等温线，需要补充一致的质量和能量闭合及相应参数；本轮不凭缺失数据制造唯一修正时长。

## 4　文献依据与长时通量

文献[1]的PDF页3–5提供圆柱控制体、中心零通量、表面第三类边界和径向加权平均的处理依据。本文保留其守恒思路，不照搬香蕉拟合参数、收缩关系、表观热扩散率或以m/s计的换热系数，也不将短时谐均通量验收推广到数天。

文献[2]的PDF页3–6支持使用局部温度、含水率相关扩散及散度形式，同时提醒平衡含水率边界的物理含义。本文重新核对温标、外法向符号和储存项，没有把文中的气相边界或可能混淆的焓单位直接移植到药材模型。

文献[3]的PDF页4–7以解吸等温线和热量闭合连接气固边界，并在移动域上描述干燥。它说明扩展模型需要哪些额外数据；本文仅借鉴隐式积分和表面加密的数值思路，不以其体积水浓度或移动边界替代本题固定域干基变量。

对文献[4]实际阅读作者v5：页2式(1.3)为exp(−1/p)，页5–6式(2.6)–(2.7)说明高对比平均系数误差，页17–18图16–18展示超慢扩散数值伪影。令p=C/0.45可识别同型浓度因子，但该文不证明本题Robin圆柱的时长。

本题达到阈值前C保持正值，D虽有强烈衰减，却未在计算范围内变为零。论文[4]的结论不能简化为“谐均必错”或“改成算术均值即可”。因此本轮检查实际事件、剖面与通量收敛，并将积分通量与独立空间离散相互比较。

将D分离为A(T_K)f(C)，通过直接积分得到下式。此式是对本题方程的自主推导，不宣称来自文献[4]的药材算法。E₁为标准指数积分，F严格单调，F′(C)=f(C)>0，从而可以构造保持通量方向的非线性面通量。

$$A(T_K)=2.4\times10^{{-3}}e^{{-3850/T_K}},\quad f(C)=e^{{-0.45/C}},\quad F(C)=Ce^{{-0.45/C}}-0.45E_1(0.45/C).$$

$$J_{{i+1/2}}=\frac{{r_{{i+1/2}}A(T_{{K,i+1/2}})}}{{r_{{i+1}}-r_i}}\left[F(C_i)-F(C_{{i+1}})\right],\quad T_{{i+1/2}}=(T_i+T_{{i+1}})/2.$$

非等温时仅在面上近似温度因子，不将∂r[AF]错当成A∂rF。相邻F值接近时以四点Gauss积分计算差值，避免消减误差；没有夹截C、人为设置D下限或跳过失败步。对原始谐均方案的比较保留在验证目录中。

## 5　离散、独立参考与终止事件

主方法为顶点型双控制体有限体积法，使用r_i=R[1−(1−i/N)²]的表面加密网格。中心控制体按圆柱体积积分，不在r=0使用奇异差商；表面节点属于半控制体，外表面Robin通量与内部面通量共同更新该状态。

主计算采用N=2048、全程耦合BDF、解析稀疏Jacobian。相对容差2×10⁻¹²，T、C绝对容差分别2×10⁻¹²与2×10⁻¹⁴；前4小时最大步长15秒，其后60秒。内部自适应步长与Excel规定的60秒采样是不同概念。

独立参考采用x=(r/R)²下的全局Chebyshev配置法，对F(C)求导构造A∂xF，再作散度。它不复用有限体积控制体、面平均或空间算子；表面通过耦合Robin方程代数消元。分别实际运行80阶Radau和160阶BDF至完整事件。

独立参考的实际表面求根均无需备用分支搜索，标量边界导数保持正值，最大水分边界残差约10⁻¹⁷量级。关键时刻还搜索F插值多项式全部实驻点，未发现节点间遗漏的更湿峰值，而非仅看21个展示半径。

定义全域最大值M(t)=max C及g(t)=M(t)−0.15。连续下穿的临界时刻为t*=inf{{t:M(t)<0.15}}，通常在界限处M=0.15，本身不是严格合格点。事件在求解器连续解上定位，未以首个整分钟合格样本替代根。

主离散的每个内部面通量均从高C指向低C，环境值始终低于阈值，因此处于阈值附近的全局最大值不能由内扩散或边界输入向上越界。实际检查所有内部节点及每个接受步的中点，并用r²上的保形PCHIP重构保证区间内不超过节点最大值。

本轮径向不增性仅出现约4×10⁻¹⁵的浮点量级偏差；临界位置为r=0。保存了完整内部网格的事件两侧、根与执行端点状态。严格判断使用未舍入数据，下面的0.02秒夹逼是半离散连续解证据，不冒充连续PDE的区间误差定理。

| 事件记录 | 时间/s | 全网格最大含水率/(kg/kg) |
|---|---:|---:|
| 根左侧 | {e['t_minus_s']:.14f} | {e['max_minus']:.17f} |
| 临界等式根 | {e['critical_s']:.14f} | {e['critical_max']:.17f} |
| 根右侧 | {e['t_plus_s']:.14f} | {e['max_plus']:.17f} |
| 正式执行端点 | {e['execution_s']:.8f} | {e['execution_max']:.17f} |

临界下降斜率为{e['critical_slope_kgkg_s']:.12e} kg/(kg·s)。综合实际空间、时间及独立方法差异，采用0.03秒工程数值误差预算，再向上取到0.0001小时网格。该预算不含未来环境、端部或物理模型的不确定性，也不是区间算术证明。

$$t_{{\rm end}}=0.36\left\lceil\frac{{t_*+0.03}}{{0.36}}\right\rceil={e['execution_s']:.2f}\ \mathrm s={e['execution_h']:.4f}\ \mathrm h.$$

## 6　表5　药材烘干过程的水分浓度

表内浓度单位为kg/kg，时间从烘干开始累计。前九行对应6、12、…、54小时，最后一行与result3.xlsx完全一致，采用严格合格执行端点。最后中心显示0.1500是四位小数舍入结果，实际值低于0.15，不能以显示值反判为未达标。

{t5}

## 7　空间、时间、独立方法与收支验收

以下是本轮实际事件，不是交接先导值。相同时间设置的网格序列观察阶分别为{conv['observed_orders'][0]:.4f}和{conv['observed_orders'][1]:.4f}，已呈现约二阶行为。最后两行单独收紧时间设置，用于分离时间误差，不拿求根容差冒充整体精度。

{grids}

细网格空间误差诊断约{conv['estimated_fine_spatial_error_s']:.6f}秒，固定网格改变时间设置的最大事件变化约{conv['measured_time_setting_change_s']:.6f}秒。Richardson仅作诊断得到{conv['richardson_diagnostic_s']:.6f}秒；正式表格仍取直接积分状态，未以外推结果替代未经检验的全场。

80阶Radau和160阶BDF参考与主解的临界差分别为{s['independent'][0]['critical_time_difference_s']:.6f}秒、{s['independent'][1]['critical_time_difference_s']:.6f}秒。6小时表格常规行最大水分差约1.17×10⁻⁸，四位显示全部一致；参考算法全程从0秒耦合积分，并非只换主方法的时间积分器。

另将两种独立参考保存的完整内部状态继续积分到正式206906.76秒端点，再逐点比较21个半径和连续重构极值。两种参考均严格低于0.15，终点剖面四位显示一致；见validation/independent_endpoint_comparison.json。

本轮在相同加密网格上还实际运行谐均通量。512、1024区间相对积分通量的事件差分别约2.5500和0.6375秒，随加密约缩小四倍。因此不能说谐均方法不收敛；积分通量在本算例具有更小的事件偏差，也未把论文中的振荡虚称为本轮已观察现象。

前3小时每60秒、21个半径回归Q2未舍入结果，最大温差{r['max_temperature_error_K']:.3e} K，最大含水率差{r['max_moisture_error_kgkg']:.3e}。原论文两张表共60个值四位显示全部一致；较密采样仍有1个温度、3个含水率值跨越末位舍入界限，不声称逐格完全相同。

水分收支采用圆柱体积权重，并以连续时间数值积分独立累计边界流失。全程最大残差为{b['max_water_balance_kgkg']:.3e} kg/kg。热量核查积分S(C)T_t而非比较ST的首末值；最大有效热收支残差{b['max_effective_heat_balance_J_m3']:.3e} J/m³，相对量约{b['effective_heat_relative']:.3e}。

另以常系数圆柱Bessel解析级数核查空间离散，三档网格显示二阶收敛；解析Jacobian与独立方向差分、面通量守恒、恒定平衡态和F差值独立积分均实际通过。它们检验数值实现，不等于真实药材实验误差已经得到验证。

## 8　长期端部影响

有限圆柱对照取0≤z≤L/2，轴线与中面对称，侧面和端面均采用相同的换热、传质系数。全域最大值同时搜索径向和轴向。瞬态二维剖面不必处处径向或轴向单调，因此不把一维最湿点直觉当作二维判据。

完整40×64全耦合算例已积分到阈值。为降低细网格长时成本，另外在6小时保持完整C场并投影T至平台，最大温度改变量约1.34×10⁻⁵ K；同网格全耦合与投影事件仅相差0.000149秒，且主答案本身完全未采用该等温简化。

{geo}

比较必须使用相同径向网格的一维、二维时长差，不能把粗二维与细一维的总差都归因于端部。径向40加密至80，端部修正只变化约0.0034秒；轴向64加密至128，修正变化约0.145秒。现有结果支持端部约提前7.5—7.7秒，非零但小于边界延拓效应。

所以本题径向表格仍以轴向均匀模型作为明确主口径，二维仅作为几何敏感性证据。并未声称有限圆柱已达到0.0001小时精度。80×128全耦合试算被内存限制中断，其日志及失败状态保留，绝不计入已完成事件或通过数量。

## 9　未来边界及传递系数敏感性

以下情景在同一N=512网格从0秒实际求解，故相对变化不会混入主网格不同造成的误差。平台假设仅作用于4小时之后；传递系数变化作用于整个过程，均没有拟合内部实验数据，也没有调参以满足背景的天数描述。

{scene}

末值保持比均值保持约提前18.28分钟，而名义50℃、0.05平台与均值保持只差约6.11秒。未来控制日志的缺失远大于本轮求解器的数值误差。表中的情景范围不构成统计置信区间，不能据此声称真实烘房必在该范围内达标。

h_m降低20%约增加1.6964小时，提高20%约缩短1.0392小时；h_T的同幅变化只产生约分钟量级影响。传质系数及气固边界映射仍是重要物理假设。若未来环境的等效平衡含水率不低于0.15，原模型甚至可能无法达到严格终止条件。

## 10　干燥机制与结束行

表面降至0.15的时刻约{mech['surface_015_time_s']/3600:.4f}小时，体积平均降至0.15约{mech['mean_015_time_s']/3600:.4f}小时，而轴心决定约57.4740小时的最终界限。只以表面或平均量判定，会把结束时间显著提前；这不是四位小数或输出采样造成的差异。

到18小时，中心仍约0.2988，此后降到0.15又需约39.47小时，占总时长约{100*mech['fraction_of_total_time_after_18h']:.1f}%。升温通过exp(−3850/T_K)加快扩散，失水通过exp(−0.45/C)抑制扩散；后期温度已近平台，后者主导了长尾。

结束时轴心D约{mech['snapshots'][-1]['center_D']:.3e} m²/s，表面D约{mech['snapshots'][-1]['surface_D']:.3e} m²/s，表面仍保持正的水分外流。数值上不能因D很小就令其为零或设置下限，也不能把R²/D直接当总时长，因为D随位置、时间及浓度持续变化。

Excel从60秒开始，每60秒一行，最后完整分钟为206880秒，随后仅补206906.76秒的执行结束行；没有额外写入更晚的206940秒。0秒初态另存NPZ。工作表共3450行、22列，其中3449行数据、72429个水分数值单元格，均设置0.0000显示格式。

正式文件已经独立按OOXML逐单元格回读，所有时间、半径、数值类型、浓度值及末行与未舍入数组一致，最大读回误差为0。模板省略号已清除。显示精度、数值离散误差和真实物理预测误差是三个不同层次，不把格式一致视为实验验证。

## 11　复现与研究边界

完整运行入口和命令见README，事件证据见output/end_event.json，全部内部状态见output/main.npz，验证数据见validation。输出必须写入新目录；原附件、第二问原交付与交接包均保持不变，也没有向远程仓库推送任何内容。

可定量支持的是所选有效模型及边界情景下的数值结果。尚无后续环境实测、药材内部水分或失重数据用于物理预测验收；真实吸附平衡、潜热闭合和收缩会改变时长。第四问应另行处理收缩，不能把本问的精确求根包装成所有物理假设均已证实。

## 参考文献与实际阅读范围

{refs}

三篇干燥论文采用上游同哈希逐页原文提取文本阅读相关部分；本轮未成功下载其原始PDF，未把提取中的疑似乱码当作可靠公式。Maddix作者v5已在线解析并截图核对指定页。访问过程、具体边界与哈希证据见source_access.md及literature/文献实际阅读与采用.md。
'''
 (p/'第三问分析与最终答案.md').write_text(text,encoding='utf-8')
 (p/'output/table5.md').write_text('# 表5　药材烘干过程的水分浓度\n\n主情景：末1小时均值保持、轴向均匀固定几何；单位kg/kg，末行为严格执行时刻。\n\n'+t5,encoding='utf-8')
 readme=f'''# q3_final_delivery

## 最终答案

主情景为前4小时原始观测线性插值、以后保持末1小时均值，附录3物性从0秒使用，固定几何并忽略端部交换。临界时长 **57.4740 h**；正式表5与result3.xlsx结束于 **57.4741 h = 206906.76 s**，该时刻全网格最大含水率 **{e['execution_max']:.17f} < 0.15**。

这是一维轴向均匀有效模型的结果，不是脱离假设的实测时长。长时二维匹配网格比较显示端部约提前7.5—7.7秒；最后观测值保持与末段均值保持则相差约18.28分钟。四位小时格式不代表真实环境与几何也具有同等预测精度。

## 文件入口

| 文件 | 内容 |
|---|---|
| 第三问分析与最终答案.md | 可用于论文的模型、求解、表5、验证及限制 |
| result3.xlsx | 正式数值工作簿，Sheet1，3450×22，已全量独立回读 |
| output/table5.csv、table5.md | 6小时表及统一结束行；CSV保存未舍入数值 |
| output/main.npz | 初态、全部60秒内部网格、21半径输出、关键状态、事件两侧与执行端点 |
| output/end_event.json | 未舍入根、两侧最大值、数值预算及执行端点 |
| output/result3_unrounded.csv、curves.npz、*.png | 完整数值、时间曲线、径向剖面及二维对照 |
| validation/ | 空间、时间、独立参考、几何、边界、收支、算子和Excel回读证据 |
| source_access.md、inputs/UPSTREAM_MANIFEST.sha256 | 实际提交、读取途径、原始哈希和文献可用性边界 |
| source/、run_all.py | 本轮真实求解器、独立参考、验收、制表及复现入口 |

## 运行环境与命令

数值环境：Python 3.13.5，NumPy 2.3.5，SciPy 1.17.0；图形依赖Matplotlib。科学计算依赖见requirements.txt。正式Excel由artifact_tool生成；普通本地环境可用已通过内存序列化及全量数值回读测试的标准库OOXML导出，不需要Office或额外电子表格包。

```bash
python -m pip install -r requirements.txt
# 从原附件重新计算全部成功数值算例，顺序执行，避免多进程内存峰值
python run_all.py --out ../q3_rerun --scope full --excel-engine portable
# 只重算主模型、导出表5/Excel和端点，不能称为新一轮完整长期验收
python run_all.py --out ../q3_main_rerun --scope main --excel-engine portable
# 对现有交付执行独立验证；不会重算全部场景
python run_all.py --scope verify
```

完整数值套件按已成功算例配置编排，不重跑被内存限制中断的80×128全耦合试算。单个主计算积分约108秒，几何算例更耗时；实际运行时间取决于硬件、线性代数库和线程设置。建议顺序运行或最多两个数值进程，Excel导出放在所有大算例之后。

从单个配置运行：

```bash
python source/q3_solver.py --config validation/configs/main.json --out ../new_main --input inputs/attachment1.xlsx
python source/q3_reference.py --n 80 --method Radau --out ../new_reference80 --input inputs/attachment1.xlsx
python source/validate_results.py --xlsx-only
```

主配置的206906.76秒执行端点来自本次输入的收敛预算与量化规则，不是物理调参。改变原始数据、未来边界或传递系数后应重新求根及决定结束行，不能沿用该端点。普通情景配置不固定执行时间，默认导出其根右侧0.01秒的半离散合格状态。

## 实际验收摘要

主解与两种独立配置的临界差小于0.0064秒；6小时常规表格的水分差约1.17×10⁻⁸。水分累计收支残差{b['max_water_balance_kgkg']:.3e}，有效热量相对残差{b['effective_heat_relative']:.3e}。前3小时回归不掩盖极少数末位舍入差异，详细数目见validation/q2_regression.json。

result3.xlsx独立读取了全部72429个水分单元格，数值和未舍入数组完全一致；3449个时间值及21个半径也通过检查。最后一行是第3450行，不是模板示例行数。最末中心显示0.1500但原值严格小于0.15，未以显示值作达标判断。

来源提交：`ab45397ce383fd968256997d61e3b701c8a9ac5f`。上传ZIP的153项清单文件逐一验证通过；原资料未覆盖，远程仓库未写入。包内MANIFEST.sha256核查最终交付自身，inputs/UPSTREAM_MANIFEST.sha256核查上游交接资料，两者用途不同。

## 不应扩大解释的结论

0.03秒是根据实际收敛和独立算法差异采用的工程数值预算，不是连续PDE的区间算术误差证书，更不是实际药材预测的置信区间。未来环境、气固边界映射、传质系数、潜热闭合和收缩仍需新数据验证；本问不得直接替代第四问。
'''
 (p/'README.md').write_text(readme,encoding='utf-8')
 return {'table_rows':len(s['table5']),'report_characters':len(text)}

if __name__=='__main__':
 import argparse
 ap=argparse.ArgumentParser();ap.add_argument('--root',type=Path,default=Path(__file__).resolve().parents[1]);args=ap.parse_args();figures(args.root);print(generate(args.root))
