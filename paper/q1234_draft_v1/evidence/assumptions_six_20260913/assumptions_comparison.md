# 六条模型假设：新旧全文

基线：`d5787b1c21856049f6e234588cad389587b7f1eb`。旧稿其余必要约定迁入第五章，详见修订记录。

## 原八条

```tex
\section{模型假设}
\label{sec:assumptions}
\begin{enumerate}
\item \textbf{药材视为初始温湿均匀的轴对称连续介质，采用中截面径向模型：}\label{ass:midsection}
主模型忽略端面，温度、含水率及局部物性仅随径向位置和时间变化；题表的“到药材中心距离”按轴向中截面内的径向位置解释。
\item \textbf{表面交换采用线性Robin形式：}
表面与烘房之间的传热、传质通量分别正比于表面与环境的温度差和有效含水率差。
\item \textbf{各问沿用同一组表面交换系数：}
后问未另给时沿用附录2的取值；$h_T$按单一系数处理，不另区分对流与辐射项。
\item \textbf{表面传质以有效材料干基驱动表示：}
取$b=g(y_a,T_s,\ldots)$，现行计算取恒等映射$g(y_a,\ldots)=y_a$。
\item \textbf{内部相对干骨架的传质仅为扩散：}
不考虑压力驱动流动及流体相对干骨架的内部对流；烘房环境量在空间上均匀，用单一的温度与空气水分量代表。
\item \textbf{题给密度仅用于有效热容量，干质量独立记账：}
题给$\rho c_p$记为有效热容量$\rhoe c_p$，真实干质量由$\rhod$另行描述；本模型不显式计入蒸发潜热、液态扩散携焓与机械功项。
\item \textbf{前三问几何固定，第四问为恒长度均匀径向收缩：}
前三问干骨架静止；第四问材料随外半径作同比例径向运动、长度取$L=L_0$，表面位置按附件2的半径记录给定。
\item \textbf{环境与半径输入采用分段线性插值和后段均值平台：}
观测区间内按环境与半径记录点分段线性插值；4\unit{h}后假定环境维持末小时（3--4\unit{h}，61个采样点）的算术均值
\begin{equation}
T_a=49.9989344262\celsius,\qquad b=0.04998754098\unit{kg/kg}.
\label{eq:future}
\end{equation}
\end{enumerate}

\Needspace{22\baselineskip}
```

## 用户确认的六条及保留公式

```tex
\section{模型假设}
\label{sec:assumptions}
\begin{enumerate}
\item \textbf{假设药材为轴对称连续介质，初始温度、干基含水率及干密度在空间上均匀分布。}\label{ass:midsection}
主模型采用中截面径向近似，忽略端面影响。
\item \textbf{假设烘房环境在空间上均匀，题给空气水分量可等效作为药材表面传质的有效环境边界量。}
\item \textbf{假设药材表面的传热、传质通量分别与温度差和有效含水率差成正比，各问沿用同一组恒定交换系数。}
\item \textbf{假设烘干过程中药材干物质质量守恒，题给密度仅用于有效热容量。}
模型不显式计入水分蒸发潜热、水分迁移携焓及机械功。
\item \textbf{前三问假设药材尺寸保持不变；第四问假设药材长度不变，并随观测半径作均匀径向收缩。}
\item \textbf{假设4\unit{h}后烘房环境保持稳定，其温度和空气水分量取3--4\unit{h}观测数据的算术平均值。}
按末小时61个采样点计算，相应环境平台为
\begin{equation}
T_a=49.9989344262\celsius,\qquad b=0.04998754098\unit{kg/kg}.
\label{eq:future}
\end{equation}
\end{enumerate}

\Needspace{22\baselineskip}
```
