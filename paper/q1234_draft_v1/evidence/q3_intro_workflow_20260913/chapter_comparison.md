# 第三问章首与流程图修订源码差异

```diff
--- before/q3.tex
+++ after/q3.tex
@@ -1,10 +1,25 @@
 \section{问题三：由全域含水率约束确定干燥时长}
 \label{sec:q3}
+
+\begingroup
+% Local spacing accommodates the added introduction without changing text size.
+\setlength{\parskip}{2pt plus 1pt minus 1pt}
+\setlength{\abovedisplayskip}{8pt plus 2pt minus 2pt}
+\setlength{\belowdisplayskip}{8pt plus 2pt minus 2pt}
+\setlength{\abovedisplayshortskip}{6pt plus 2pt minus 1pt}
+\setlength{\belowdisplayshortskip}{6pt plus 2pt minus 1pt}
+问题三在问题二变物性热质耦合模型的基础上，进一步确定满足含水率要求的干燥时长。
+本问保持控制方程、物性关系与环境边界不变，沿用同一初态下的温湿联合轨迹。
+在一维径向模型中，以全径向最大含水率严格低于$0.15\unit{kg/kg}$为终止要求，
+不以表面含水率或截面平均值代替最大值。先通过下降穿越检测与括区求根定位候选等号根，
+再以径向重构极值复核；结合网格加密和独立积分对照设置经验数值余量，
+选取并复核严格满足阈值要求的执行点，给出所设环境条件下的模型干燥时长与径向含水率分布。
+求解流程见图\ref{fig:q3-workflow}。
 
 \begingroup
 \setlength{\intextsep}{10pt}
 \begin{figure}[H]
-\centering\includegraphics[width=\linewidth]{figures/question_workflows/q3_workflow.pdf}
+\centering\includegraphics[width=\linewidth]{figures/q3_intro/q3_workflow.pdf}
 \caption{问题三的一维径向终点判定流程}
 \label{fig:q3-workflow}
 \end{figure}
@@ -143,7 +158,7 @@
 末行轴心显示为0.1500，是式\eqref{eq:q3-end-moisture}的四位舍入值；
 达标判断使用未舍入场而不使用表格显示值。
 160阶空间加密参考和另一隐式时间方法在全部72429个规定水分输出上四位一致，
-其中空间加密参考与正式轨迹的最大未舍入差约
+\mbox{其中空间加密参考}与正式轨迹的最大未舍入差约
 $9.33\times10^{-9}\unit{kg/kg}$。
 该结果支持已选方程的数值稳定性，不替代物理参数验证。
 
@@ -185,3 +200,5 @@
 该单因素情景为人为设定而非观测误差范围（见第\ref{sec:environment-scenarios}节）。
 故57.4741\unit{h}应与环境平台和有效气固边界共同报告，
 不能仅凭小数位数给出真实工况下的确定性保证。
+
+\endgroup
```
