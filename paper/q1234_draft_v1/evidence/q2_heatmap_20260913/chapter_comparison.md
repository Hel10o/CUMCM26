# 图5替换对应的源稿差异

除图路径、图注和一个读图段外，本章其余文字及局部排版参数保持。

```diff
--- before.tex
+++ q2.tex
@@ -171,13 +171,13 @@
 
 \begin{figure}[!htb]
 \centering
-\includegraphics[width=0.94\textwidth]{figures/font_revision/q2_profiles.pdf}
-\caption{第二问前3小时的温湿状态路径与径向含水率。左图连接轴心和表面的已存温湿状态，箭头表示时间推进；右图保留中截面径向剖面，双向箭头标示末时轴心与表面含水率差。}
+\includegraphics[width=0.94\textwidth]{figures/q2_heatmap/q2_fields.pdf}
+\caption{第二问前3小时径向温度场与干基含水率场的时空演化。横轴为时间，纵轴为径向位置，颜色表示场量大小；等值线辅助辨识时空分布，末时径向差值另作标注。}
 \label{fig:q2-profiles}
 \end{figure}
 
-图\ref{fig:q2-profiles}左图把升温与失水放在同一路径中，轴心初期以升温为主，表面则较早出现含水率下降；右图表明，初期失水集中于外层，随后内部含水率逐步
-降低。
+图\ref{fig:q2-profiles}左图显示温度总体随时间升高，并逐渐趋于径向均匀；
+右图显示含水率先在表层下降，低含水区域随后向内部扩展，径向差异仍较明显。
 
 第二问$0.5\unit{h}$轴心温度32.1892\celsius，低于第一问同一
 时刻；这是从初态使用不同物性、尤其初始有效热容量更大的正常结果，

```
