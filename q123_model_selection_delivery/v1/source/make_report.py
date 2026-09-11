"""Build quantitative review and plots solely from saved unrounded outputs."""
from pathlib import Path
import json,hashlib
import numpy as np,pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from analyse import load,scalar,profile,ROOT
P=ROOT;A=P/'analysis';figdir=P/'figures';figdir.mkdir(exist_ok=True)
s=pd.read_csv(A/'stage_summary.csv');ev=pd.read_csv(A/'event_times.csv');norm=pd.read_csv(A/'midplane_difference_norms.csv');pc=pd.read_csv(A/'paired_convergence.csv');sn=pd.read_csv(A/'equilibrium_sensitivity.csv');val=pd.read_csv(A/'conservation_runs.csv')

def md(headers,rows):
 return '|'+ '|'.join(headers)+'|\n|'+'|'.join(['---']*len(headers))+'|\n'+''.join('|'+ '|'.join('—' if str(x)=='nan' else str(x) for x in row)+'|\n' for row in rows)
def by(q,g):return s[(s.question==q)&(s.group==g)].iloc[0]
def event(g):return float(ev[ev.group==g].equal_s.iloc[0])
def texfmt(x,n=4):return f'{x:.{n}f}'
sourcefig=[]
def savefig(name,cases):
 plt.tight_layout();plt.savefig(figdir/name,dpi=160,bbox_inches='tight');plt.close();sourcefig.append(dict(figure=name,cases=cases))
for q,stage in [(1,1800),(23,10800)]:
 names=['q1_B_r512_v2','q1_F00_r96_z0_v2','q1_F10_r96_z128_v2','q1_F01_r96_z0_v2','q1_F11_r96_z128_v2'] if q==1 else ['q23_B_r512_v2','q23_F00_r96_z0_v2','q23_F10_r96_z128_retry','q23_F01_r96_z0_v2','q23_F11_r96_z128_v2']
 cases=[load(n) for n in names]
 for field,unit in [('T','Temperature (deg C)'),('C','Dry-basis moisture (kg/kg)')]:
  plt.figure(figsize=(7.2,4.6))
  for g,c in zip(['B','F00: 1D, off','F10: 2D, off','F01: 1D, latent','F11: 2D, latent'],cases):
   rr=np.linspace(0,.02,201);plt.plot(rr*100,profile(c,stage,field,rr),label=g)
  plt.xlabel('Radius at midplane (cm)');plt.ylabel(unit);plt.title(f'Q{1 if q==1 else 2}, t={stage/3600:g} h; conditional F');plt.legend();savefig(f'Q{1 if q==1 else 2}_midplane_{field}.png',names)
 plt.figure(figsize=(7.2,4.6))
 for g,c in zip(['B, effective','F00','F10','F01','F11'],cases):
  d=c['data'];sel=d['time']<=stage;ix=list(d['metric_names']).index('Mwater');loss=(c['result']['initial']['Mwater']-d['metrics'][sel,ix])*1000;plt.plot(d['time'][sel]/3600,loss,label=g)
 plt.xlabel('Time (h)');plt.ylabel('Cumulative water outflow (g)');plt.title(f'Q{1 if q==1 else 2}, whole-cylinder mass balance');plt.legend();savefig(f'Q{1 if q==1 else 2}_whole_water.png',names)
 if q==23:
  plt.figure(figsize=(7.2,4.6))
  for g,c in zip(['B','F00','F10','F01','F11'],cases):
   d=c['data'];plt.plot(d['time']/3600,d['metrics'][:,list(d['metric_names']).index('maxC')],label=g)
  plt.axhline(.15,linestyle='--');plt.xlabel('Time (h)');plt.ylabel('Full-domain max C (kg/kg)');plt.title('Q3 full-domain trajectory, Ceq=0.075 scenario');plt.legend();savefig('Q3_full_domain_maxC.png',names)
  plt.figure(figsize=(6.8,4.2));plt.bar(['Without latent: G0','With latent: G1'],[event('F10')-event('F00'),event('F11')-event('F01')]);plt.ylabel('2D minus paired 1D event time (s)');plt.title('End exchange changes with latent coupling');savefig('Q3_geometry_time_effect.png',names[1:])
  raw=np.load(P/'output/q23_F11_r96_z128_v2/solution.npz');it=int(np.where(raw['field_time']==10800)[0][0]);field=raw['fields'][it,:,:,1]
  plt.figure(figsize=(8,3.5));plt.pcolormesh(raw['z']*100,raw['r']*100,field,shading='auto');plt.colorbar(label='C (kg/kg)');plt.xlabel('z from midplane to end (cm)');plt.ylabel('Radius (cm)');plt.title('F11 moisture at 3 h: half-length axisymmetric domain');savefig('Q2_F11_full_field_C.png',['q23_F11_r96_z128_v2'])
  plt.figure(figsize=(7.2,4.6))
  for g,c in zip(['F00','F10','F01','F11'],cases[1:]):
   lg=c['ledger'];plt.plot([x['t']/3600 for x in lg],[x['energy_residual'] for x in lg],label=g)
  plt.xlabel('Time (h)');plt.ylabel('Energy residual (J)');plt.title('Independent boundary integration vs stored enthalpy');plt.legend();savefig('Q3_energy_residual.png',names[1:])
(P/'figures/figure_sources.json').write_text(json.dumps(sourcefig,indent=2))

report=['# 前三问二维与潜热影响评估\n', '> 本轮为条件模型的定量选型交付。四组均真实联立积分，原基线、旧论文与官方Excel没有覆盖。下列结果不等于药材参数已被实验识别。\n']
report+=['## 1. 比较口径\n','输入为逐字节核验的仓库环境CSV，0–4h线性插值、之后末小时61点均值。共同模型F采用固定干骨架、组分焓、气固串联阻力和理想活度族；主情景未来平衡C_eq=0.075kg/kg。F的质量、参数及能量方程见《模型推导与假设契约》。\n','F00/F10关闭潜热，是消融诊断；F01/F11开启同一界面通量对应的潜热。F00→F10、F01→F11分别为两种相变设置下的端面效应；F00→F01、F10→F11为配对潜热效应。交互项I=F11−F10−F01+F00。\n','B→F00另列为闭合调整：气固映射、串联气膜、固定干密度/容量与携焓均可能变化。尤其Q1的F容量取附录3组分比热，未保留2600常数，不能把B到F的全部差异归于潜热。B失水列是固定参考干密度换算的有效失水，不是已验证的真实干燥量。\n']
report.append('\nQ1/Q2表中的B为本轮按原有效方程新跑的回归解，不是对冻结NPZ逐元素回读。Q3事件表明确引用原正式B；本轮B512回归根为206904.693273秒，与原根约差−1.697秒，不替换原正式值。图中的B也是本轮回归轨迹。\n')
for q,caption in [(1,'Q1：1800秒'),(2,'Q2：3小时')]:
 report.append(f'## {q+1}. {caption}\n')
 rows=[]
 for g in ['B','F00','F10','F01','F11']:
  v=by(q,g);rows.append([g,*[texfmt(v[k]) for k in ['coreT','sideT','coreC','sideC','loss_g','convective_kJ']]])
 report.append(md(['组别','中截面轴心T/℃','中截面表面T/℃','轴心C','表面C','累计失水/g','对流输入/kJ'],rows))
 a,b,c,d=[by(q,g) for g in ['F00','F10','F01','F11']]
 report.append(f"端面交换使无潜热组的总体失水增加{b.loss_g-a.loss_g:.6f}g（{100*(b.loss_g/a.loss_g-1):.3f}%），使有潜热组增加{d.loss_g-c.loss_g:.6f}g（{100*(d.loss_g/c.loss_g-1):.3f}%）。有潜热F11的端面净失水为{d.end_loss_g:.6f}g，占其全表面净流出的{100*d.end_loss_g/d.loss_g:.3f}%；这个占比不等于二维与一维的总差。\n")
 report.append(f"一维潜热效应F01−F00：中截面轴心温度{c.coreT-a.coreT:+.6f}℃，表面温度{c.sideT-a.sideT:+.6f}℃；轴心C变化{c.coreC-a.coreC:+.6f}，表面C变化{c.sideC-a.sideC:+.6f}kg/kg；总体失水减少{a.loss_g-c.loss_g:.6f}g（{100*(1-c.loss_g/a.loss_g):.3f}%）。\n")
 report.append(f"F11端面轴心温度为{d.end_centerT:.6f}℃、含水率为{d.end_centerC:.6f}kg/kg；与中截面轴心的差分别为{d.end_centerT-d.coreT:+.6f}℃和{d.end_centerC-d.coreC:+.6f}kg/kg。因此，中截面相近不能外推为端部或整个物体都相近。\n")
 report.append(f"F11的模型能量账本：对流输入{d.convective_kJ:.6f}kJ=储能增加{d.stored_kJ:.6f}kJ+潜热{d.latent_kJ:.6f}kJ+净水携焓{d.sensible_out_kJ:.6f}kJ（差值为积分残差）。F00虽满足消融方程，但相对于真实相变账本还漏掉{a.physical_phase_kJ:.6f}kJ，不能称为真实蒸发能量闭合。\n")
 rows=[]
 for label,aa,bb in [('闭合 B→F00',by(q,'B'),a),('G0',a,b),('G1',c,d),('L1',a,c),('L2',b,d)]:
  rows.append([label,f'{bb.coreT-aa.coreT:+.6f}',f'{bb.sideC-aa.sideC:+.6f}',f'{bb.loss_g-aa.loss_g:+.6f}',f'{bb.convective_kJ-aa.convective_kJ:+.6f}'])
 rows.append(['I',f'{d.coreT-b.coreT-c.coreT+a.coreT:+.6f}',f'{d.sideC-b.sideC-c.sideC+a.sideC:+.6f}',f'{d.loss_g-b.loss_g-c.loss_g+a.loss_g:+.6f}',f'{d.convective_kJ-b.convective_kJ-c.convective_kJ+a.convective_kJ:+.6f}'])
 report.append(md(['对照','轴心ΔT/℃','表面ΔC','Δ失水/g','Δ对流/kJ'],rows))
 if q==1:
  report.append('旧B轨迹上的条件潜热45.5923kJ与对流4.800979kJ之比9.49647，仅诊断旧轨迹能量缺项。新F01同时降低失水和表面温度，因此失水约1.214g、潜热约2.949kJ，对流反而增加至约7.063kJ。不能维持旧18.609g失水只减潜热，也不能以9.5倍推断时长。\n')
 report.append(f"![中截面温度](figures/Q{q}_midplane_T.png)\n\n![总体失水](figures/Q{q}_whole_water.png)\n")
report+=['## 4. Q3：全域事件、闭合改变与交互\n']
rows=[['B原正式值（继承）','206906.389932','57.473997','206906.76（旧模型口径）']]
for g in ['F00','F10','F01','F11']:
 v=ev[ev.group==g].iloc[0];rows.append([g,f'{v.equal_s:.6f}',f'{v.equal_h:.6f}',f'{v.execution_s:.6f}'])
report.append(md(['组别','等号临界/s','等号临界/h','本轮真实续算执行/s'],rows))
b0=206906.38993234557;g0=event('F10')-event('F00');g1=event('F11')-event('F01');l1=event('F01')-event('F00');l2=event('F11')-event('F10');inter=g1-g0
report.append(f"相对于原B，共同闭合调整B→F00为{event('F00')-b0:+.6f}s（{(event('F00')-b0)/3600:+.6f}h）；一维潜热效应为{l1:+.6f}s（{l1/3600:+.6f}h），二维潜热效应为{l2:+.6f}s。不能将这些差合并后全部称作潜热效应。\n")
report.append(f"无潜热时端面使临界时间提前{-g0:.6f}s；有潜热时提前{-g1:.6f}s，即{-g1/60:.4f}分钟、约占一维有潜热时长的{-100*g1/event('F01'):.5f}%。交互项I={inter:+.6f}s，说明旧模型的约7.5秒端面影响不能直接沿用到潜热模型。\n")
report.append('主情景F11的最大含水率在临界附近位于中截面轴心。根后实际续算600秒，末端全域max C=0.14982902974264486。该执行时间含人为预设数值缓冲，不是最短烘干时间；不含等温线、气膜近似或未来环境的不确定性。\n')
q3=load('q23_F11_r96_z128_v2')['result'];vv=np.array(q3['cumulative']);report.append(f"F11在本轮执行端点的全域累计失水为{1000*(q3['initial']['Mwater']-q3['final']['Mwater']):.6f}g；对流输入{(vv[1]+vv[5])/1000:.6f}kJ、相变耗热{(vv[2]+vv[6])/1000:.6f}kJ、净水携焓{(vv[3]+vv[7])/1000:.6f}kJ、储能{q3['final']['enthalpy']/1000:.6f}kJ。它们与Q1采用不同初始干质量，不在1800秒接续。\n")
report.append('![全域轨迹](figures/Q3_full_domain_maxC.png)\n\n![几何—潜热交互](figures/Q3_geometry_time_effect.png)\n')
report.append('## 5. 数值分辨率与验收边界\n')
report.append(md(['nr×nz','无潜热配对端面效应/s','有潜热配对端面效应/s'],[[f'{n}×{z}',f"{pc[(pc.question==23)&(pc.nr==n)&(pc.latent==0)].end_effect_s.iloc[0]:.6f}",f"{pc[(pc.question==23)&(pc.nr==n)&(pc.latent==1)].end_effect_s.iloc[0]:.6f}"] for n,z in [(24,32),(48,64),(96,128)]]))
# Separate axial and radial refinements, all actually present at report time.
axis=[]
for q in [1,23]:
 for latent in [0,1]:
  n=f'q{q}_F1{latent}_r48_z128_axis'
  if not (P/'output'/n/'result.json').exists():continue
  ax=load(n);co=load(f'q{q}_F1{latent}_r48_z64_v2');fi=load(f'q{q}_F1{latent}_r96_z128_'+('retry' if q==23 and latent==0 else 'v2'))
  row=dict(question=q,latent=latent,axial_only_loss_g=scalar(ax,1800 if q==1 else 10800)['loss_g']-scalar(co,1800 if q==1 else 10800)['loss_g'],radial_only_loss_g=scalar(fi,1800 if q==1 else 10800)['loss_g']-scalar(ax,1800 if q==1 else 10800)['loss_g'])
  if q==23:row.update(axial_only_event_s=ax['result']['event_equal_s']-co['result']['event_equal_s'],radial_only_event_s=fi['result']['event_equal_s']-ax['result']['event_equal_s'])
  axis.append(row)
pd.DataFrame(axis).to_csv(A/'separate_axis_radial_refinement.csv',index=False,float_format='%.17g')
report.append(md(['问/潜热','单独轴向加密Δ失水/g','单独径向加密Δ失水/g','轴向加密Δt/s','径向加密Δt/s'],[[str(v['question'])+'/'+str(v['latent']),f"{v['axial_only_loss_g']:.7f}",f"{v['radial_only_loss_g']:.7f}",f"{v.get('axial_only_event_s',float('nan')):.6f}",f"{v.get('radial_only_event_s',float('nan')):.6f}"] for v in axis]))
report.append('主1D F01从48→96→192格，临界时间为264619.813184、264637.766874、264642.349085秒；独立H/C状态、单元中心、无储量表面Radau在96→192→384→768单元得到264404.372325、264569.714074、264622.673906、264638.152692秒。两种空间方法从不同边界表示向同一量级收敛，不是只换时间积分器。\n')
report.append('同96格主空间离散改用更紧Radau，根为264637.762255秒，与BDF差约0.00462秒。主96格与192格差约4.58秒，独立768格与主192格差约4.20秒。二维配对端面效应48→96格变化约0.465秒；本轮可分辨约237秒和约14小时的效应，但没有秒以下连续PDE误差保证。\n')
report.append('作为保守工程数值尺度，取最近两档原始时间差、独立方法差和配对端面变化的最大值，再留安全系数；约数十秒，而不是旧0.03秒。本轮预设600秒续算缓冲明显大于这些观测差，但不称为严格误差上界或真实工艺保证。\n')
rows=[]
for q in [1,2]:
 for g in ['G0','G1']:
  tt=norm[(norm.question==q)&(norm.contrast==g)&(norm.field=='T')].max_abs.iloc[0];cc=norm[(norm.question==q)&(norm.contrast==g)&(norm.field=='C')].max_abs.iloc[0];rows.append([q,g,f'{tt:.8g}',f'{cc:.8g}'])
report.append(md(['问','端面对照','记录时点中截面最大绝对温差/℃','最大绝对含水率差/kgkg'],rows))
report.append('关闭二维端面交换的真实退化试算，与同径向一维相比仍有约2.84×10⁻⁵℃、8.74×10⁻⁷kg/kg的自适应时间误差。故Q1及Q2有潜热时的极小中截面差不能干净分离为物理端面效应；结论是当前工程分辨率下近似等价，不是严格为零或四位完全相同。\n')
report.append('几何选型记录的工程门槛为中截面0.05℃/0.001kg/kg、时长0.1%、整体失水/能量1%。这些是先于最终选型、但在试算后提出的报告标准，并非用户给定或全体运行前预注册。即使换用更严标准，报告保留原始差值，不按是否过线隐藏变化。\n')
checks=json.loads((P/'validation/independent_checks_v1/independent_budget_checks.json').read_text());mainnames=[v['case'] for v in checks];v=val[val.case.isin(mainnames)]
report.append(f"主要四组的干质量漂移为零；独立重构几何权重、储量和表面积分已核对。主算例最大归一化水质量残差为{v.mass_relative.abs().max():.3g}，能量残差为{v.energy_relative.abs().max():.3g}；另一时间网格Simpson后处理的最大归一化能量残差为{v.energy_posthoc_relative.abs().max():.3g}，均低于运行前代码写入的2×10⁻⁵/2×10⁻³阈值。\n")
report.append('## 6. 可达性及参数依赖\n')
rows=[]
for eq in [.05,.12,.20]:
 v=sn[(sn.ceq==eq)&(sn.dimension==2)].iloc[0];rows.append([eq,'32×48',f'{v.equal_h:.4f}' if np.isfinite(v.equal_h) else '240h无下穿',f'{v.final_maxC:.9f}'])
rows.insert(1,[.075,'96×128',f"{event('F11')/3600:.6f}",f"{q3['final']['maxC']:.9f}"])
report.append(md(['假设C_eq','二维网格','等号临界/h','已积分末端max C'],rows))
report.append('0.05与0.12是较粗的敏感性算例，不冒充主网格精度。0.05的一维32→48格时长变化约0.046小时，因此更适合报告“约71小时”，不是稳定四位时长；0.12约85小时。趋势显著大于数值差，但不能把这三个时间当实验置信区间。\n')
report.append('0.20情景始终开启全域事件检查，实际计算到240h未出现下穿，最终max C约0.2000003；它同时具有高于阈值的长期平衡。未仅凭稳态值排除瞬态，未伪造结束末行。这足以说明现有材料不能识别唯一真实时长或保证0.15必可达。\n')
gas=[]
for mult in [.5,1.,2.]:
 n='q23_F01_r48_z0_v2' if mult==1 else f'q23_gas{mult:g}_1D';d=json.loads((P/'output'/n/'result.json').read_text());gas.append([mult,d['event_equal_s']/3600])
report.append(md(['气膜K_p倍数（其他不变，1D48格）','临界/h'],[[x,f'{y:.6f}'] for x,y in gas]))
report+=['## 7. 最终选型结论\n','Q1、Q2的规定径向表及机理分析推荐一维有潜热共同模型；总体水分、能量与端部状态另保留二维结果。Q3推荐用二维有潜热模型作最终全域事件判定，用一维作趋势与参数扫描。主情景中一维晚约4分钟，可作该情景的保守近似，但不能未经验证推广到其他气固参数。\n','潜热不是可删的小项。固定干骨架路线能保持质量账本闭合，但须放弃经验ρ为动态真实湿密度的解释；Q1容量与部分焓仍需明确额外假设。旧B及正式表不被本轮条件情景自动替换，不将73.4446h写成无条件真实答案。\n','论文可按“二维一般守恒模型—端面/潜热四组对照—限定指标的降维验证—一维径向机理—二维全域终判—可达性与参数局限”组织。不能用中截面差小，证明整个药材的总失水或热量差也小。\n','## 8. 证据边界与未完成项\n','本轮输入CSV已经逐字节核验，四组、参数情景、收敛和独立PDE均有新运行数据。原XLSX、冻结NPZ没有完成二进制逐元素复核，原PDF页图未完成视觉逐式核查；实际使用的原文页提取文本、出版社HTML及失败日志在来源清单中明确区分。没有声称重新验收整个历史仓库。\n','早期Q1误写D0的试算、两份超时作业、一次二维内存终止以及独立细网格初始Jacobian问题均已隔离并保留记录。最终Q1均用核对后的7×10⁻⁹从初态重算；失败或合成测试不作为物理结果。官方Excel、全文定稿和实验参数识别不是本轮已完成项。\n']
(P/'前三问二维与潜热影响评估.md').write_text('\n'.join(report),encoding='utf-8')
print('Report and plots generated from unrounded data.')
