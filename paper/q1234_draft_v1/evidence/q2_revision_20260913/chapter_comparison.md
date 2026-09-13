# 问题二本轮源稿对照

比较开始时已存在的本地章首版本与本轮修改。7.1—7.3文字、公式字节保持；排版分组扩展至本章末尾。

```diff
--- local_before.tex
+++ sections/q2.tex
@@ -2,20 +2,27 @@
 \label{sec:q2}
 
 \begingroup
+% Local white-space settings; body fonts, leading and margins are unchanged.
 \setlength{\parskip}{0pt}
-\setlength{\intextsep}{0pt}
-\captionsetup{skip=4pt}
-问题二采用附录3变物性，从共同初态联立求解固定半径下的径向温湿场，
-输出规定结果与所设环境延拓下的全程轨迹。求解流程见图\ref{fig:q2-workflow}。
+\setlength{\abovedisplayskip}{4pt}
+\setlength{\belowdisplayskip}{4pt}
+\setlength{\abovedisplayshortskip}{4pt}
+\setlength{\belowdisplayshortskip}{4pt}
+\setlength{\intextsep}{6pt}
+\setlength{\textfloatsep}{6pt}
+\setlength{\floatsep}{6pt}
+\captionsetup{skip=5pt}
+\renewcommand{\arraystretch}{1.08}
+问题二在第\ref{sec:common-model}章统一模型基础上，采用附录3变物性，从共同初态
+联立求解固定半径下的径向温湿场。通过温度与含水率对物性的反馈，
+给出规定结果及所设环境延拓下的全程轨迹，为问题三判定终点提供基础。
+求解流程见图\ref{fig:q2-workflow}。
 
 \begin{figure}[H]
-\centering\includegraphics[trim=0 6bp 0 6bp,clip,width=\linewidth]{figures/question_workflows/q2_workflow.pdf}
-\caption{问题二求解流程}
+\centering\includegraphics[width=\linewidth]{figures/q2_revision/q2_workflow.pdf}
+\caption{问题二由统一模型到变物性热质耦合模型的求解流程}
 \label{fig:q2-workflow}
 \end{figure}
-% Rebalance only the opening block's white space; subsequent source is unchanged.
-\vspace{-11pt}
-\endgroup
 
 \subsection{从通用方程到变物性耦合系统}
 第二问从共同初态开始，全程使用附录3物性\cite{problem}，不接续第一问
@@ -140,14 +147,14 @@
 温湿数值。逐秒评价联合连续解，不将不同模型的温度、水分拼接。
 
 \subsection{规定表格及空间规律}
-\begin{table}[htbp]
+\begin{table}[!htb]
 \centering\small
 \caption{3小时内药材中截面温度（$^\circ$C）}
 \label{tab:q2-temperature}
 \input{tables/q2_temperature.tex}
 \end{table}
 
-\begin{table}[htbp]
+\begin{table}[!htb]
 \centering\small
 \caption{3小时内药材中截面干基含水率（kg/kg）}
 \label{tab:q2-moisture}
@@ -162,16 +169,17 @@
 $1.3825\unit{kg/kg}$，相对初始含水率下降45.7833\%。该比例是固定参考
 干密度下的有效水分减少比例，不是实测总质量损失率。
 
-\begin{figure}[htbp]
+\begin{figure}[!htb]
 \centering
 \includegraphics[width=0.94\textwidth]{figures/font_revision/q2_profiles.pdf}
 \caption{第二问前3小时的温湿状态路径与径向含水率。左图连接轴心和表面的已存温湿状态，箭头表示时间推进；右图保留中截面径向剖面，双向箭头标示末时轴心与表面含水率差。}
 \label{fig:q2-profiles}
 \end{figure}
 
-\Needspace{5\baselineskip}
 图\ref{fig:q2-profiles}左图把升温与失水放在同一路径中，轴心初期以升温为主，表面则较早出现含水率下降；右图表明，初期失水集中于外层，随后内部含水率逐步
-降低。第二问$0.5\unit{h}$轴心温度32.1892\celsius，低于第一问同一
+降低。
+
+第二问$0.5\unit{h}$轴心温度32.1892\celsius，低于第一问同一
 时刻；这是从初态使用不同物性、尤其初始有效热容量更大的正常结果，
 不是问间接口错误。第一问和第二问是不同参数情形，不能共用一段预热轨迹。
 
@@ -189,7 +197,15 @@
 $H$度量沿当前轨迹的累计温度贡献，$M$度量累计含水率贡献；这是代数
 分解，不能当作独立改变某一因素的因果贡献百分比。
 
-\Needspace{7\baselineskip}
+图\ref{fig:q2-mechanism}展示上述分解；前$3\unit{h}$逐秒采样中，轴心与表面扩散率
+分别于约$2.46\unit{h}$和$2.02\unit{h}$达到该时段的采样峰值，随后回落。
+
+\begin{figure}[htbp]
+\centering\includegraphics[width=\linewidth]{figures/q2_revision/q2_mechanism.pdf}
+\caption{第二问前3小时轴心与表面的扩散率对数分解。$H$为温度贡献，$M$为含水率贡献，$H+M=\ln(D/D_0)$；标记为逐秒采样峰值，不表示连续时间严格极值。}
+\label{fig:q2-mechanism}
+\end{figure}
+
 $3\unit{h}$时，轴心与表面的$D/D_0$分别为2.1957与1.8207，说明相对
 初态累计升温促进仍占优势；但最后半小时，两处扩散率分别下降约1.06\%
 和3.16\%。因此“扩散系数全程单调增加”不成立。表面还曾在早期每秒
@@ -203,6 +219,8 @@
 不能替代气固水分基准识别\cite{dasilva2014,adrover2020}。
 
 \subsection{独立验证与适用范围}
+以下核查数值输出与模型账本的一致性，并检验降维适用范围。
+
 前3小时已有节点有限体积逐级加密至2560区间及Richardson外推，
 另用独立空间离散与Radau积分核对。全程轨迹与该外推轨迹在前3小时
 共同采样点的最大温差约$1.07\times10^{-9}\unit{K}$、含水率差约
@@ -225,4 +243,8 @@
 这支持中截面的工程近似，但不能保证降维后所有四位显示相同；长期全域
 达标须结合第三问终点证据，不能直接沿用前3小时的几何误差。
 本问早期大通量阶段亦受相变能量缺口约束，相关量级诊断与闭合限制见第\ref{sec:limitations}节。
+
+综上，温湿场响应不同步，升温促进与失水抑制呈阶段性竞争；
+所得同一条轨迹为问题三追踪径向最大含水率、判定干燥终点提供计算基础。
 \FloatBarrier
+\endgroup

```
