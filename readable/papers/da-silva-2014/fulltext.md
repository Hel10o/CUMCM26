# Estimation of thermo-physical properties of products with cylindrical shape during drying: The coupling between mass and heat

此文件是本地原始 PDF 的自动全文提取，不是摘要或模型生成的论文内容。页码为 PDF 物理页序号（从1开始），可能与印刷页码不同。正文可检索；公式上下标、分式、表格列关系和图中信息仍须对照原始页面，不要据提取文本声称已完成逐式或图像核验。⟦U+xxxx⟧是原PDF未可靠解码的字符标记，不是数学变量，不能直接删去。

原件：[PDF](../../../%E5%88%86%E6%9E%90%E4%B8%8E%E6%96%87%E7%8C%AE/1-s2.0-S0260877414002118-main.pdf)

DOI：[10.1016/j.jfoodeng.2014.05.010](https://doi.org/10.1016/j.jfoodeng.2014.05.010)

原件 SHA-256：`f366438e9b447e270ae210f0f7e8bcc59bb65c94e850736e8db992e8817deb5b`

共 9 页；正文提取模式：`raw`。

## PDF 第 1 页

```text
Estimation of thermo-physical properties of products with cylindrical
shape during drying: The coupling between mass and heat
Wilton Pereira da Silva ⇑
, Cleide M.D.P.S. e Silva, Fernando J.A. Gama
Center of Sciences and Technology, Federal University of Campina Grande, PB, Brazil
a r t i c l e i n f o
Article history:
Received 21 March 2014
Received in revised form 5 May 2014
Accepted 11 May 2014
Available online 20 May 2014
Keywords:
Heat and mass transfer
Liquid diffusion model
Shrinkage
Variable properties
Finite volume method
Evaluation of simpliﬁcations
a b s t r a c t
This article aimed at studying drying of products with cylindrical shape, using an apparent liquid diffu-
sion model, with coupling between mass and heat at surface of the product. Model includes variable
thermo-physical properties and shrinkage. The one-dimensional diffusion equation in cylindrical coordi-
nates, with boundary condition of the third kind (i.e., convective boundary condition), was discretized by
means of the ﬁnite volume method with a fully implicit formulation. The proposed solution can be used
to determine thermo-physical parameters, via optimization technique, and also to simulate water migra-
tion and heat transport. Developed software was applied to describe convective drying of whole bananas.
Three experiments were carried out at average drying air temperature of 47.9, 58.6 and 66.9 °C, enabling
to determine the thermo-physical properties as well as to simulate the process of heat and mass transfer.
The statistical indicators of the simulations made it possible to conclude that, for the three experiments,
the proposed model well describes the involved processes.
Ó 2014 Elsevier Ltd. All rights reserved.
1. Introduction
Food processing usually involves a stage in which heat is trans-
ferred to, and/or removed from, the product (Da Silva et al., 2011).
Preservation methods such as pasteurization and cooling, among
others, involve heat transfer. Thus, to describe these and other pro-
cesses, the thermal properties of the product should be known. If
the range of temperature involved in the process is not very large,
the thermal properties can be considered constant. Thus, this type
of processing is generally easy to be described because, in many
occasions, the mass of the product can be also considered constant
along the time as, for instance, in cooling processes. In other types
of processing, such as soaking, baking and drying, simultaneous
heat and mass transfer between the product and the external med-
ium are involved. In these cases, in order to describe such processes,
the thermo-physical properties of the product must be also known.
This type of processing is difﬁcult to be described, particularly the
heat transfer, due to the fact that the ratio water/dry matter in
the product is continually changing along the time. In the speciﬁc
case of drying, water is lost along the time, while the dry matter
does not vary during this process. As a consequence, in this case,
several properties involved in the description of the phenomenon
are variable, such as the density of the product, speciﬁc heat, ther-
mal conductivity and thermal diffusivity (Lima et al., 2002; Mariani
et al., 2008; Lemus-Mondaca et al., 2013; Perussello et al., 2013).
Particularly in the drying study of fruits, the volume and moisture
diffusivity of the product are also variable. As the drying operation
is frequently used to prolong the shelf life of agricultural products,
these properties must be known.
The post-harvest losses of agricultural products can be signiﬁ-
cantly reduced by using proper drying techniques. As above men-
tioned, the use of such techniques requires the knowledge of the
thermo-physical properties of the agricultural product. Different
approaches are used to determine thermo-physical properties
and to describe water loss (and heat transfer) during drying, and
some studies are presented in the following. In several drying stud-
ies, in order to describe heat and mass transfer using analytical
solutions of the diffusion equation, some authors such as
Ramsaroop and Persad (2012), which studied heat transfer during
drying of coconut, assume the thermo-physical properties of the
product with constant values. Wu et al. (2004) used numerical
solutions of the diffusion equation to describe heat and mass trans-
fer during drying of rice, but some thermo-physical properties of
the product were considered constant by these researchers. How-
ever, most researchers consider these properties with variable val-
ues, and use numerical solutions of the diffusion equation to
describe both: mass and heat transfer (Lima et al., 2002; Mariani
et al., 2008; Lemus-Mondaca et al., 2013; Perussello et al., 2013).
Usually the mass migration is described under isothermal
http://dx.doi.org/10.1016/j.jfoodeng.2014.05.010
0260-8774/Ó 2014 Elsevier Ltd. All rights reserved.
⇑ Corresponding author. Tel.: +55 83 3333 2962.
E-mail addresses: wiltonps@uol.com.br (W.P. da Silva), cleidedps@uol.com.br
(C.M.D.P.S. e Silva), fernando_gama@uol.com.br (F.J.A. Gama).
Journal of Food Engineering 141 (2014) 65–73
Contents lists available at ScienceDirect
Journal of Food Engineering
journal homepage: www.elsevier.com/locate/jfoodeng
```

## PDF 第 2 页

```text
conditions, i.e., this phenomenon is described, for each drying air
temperature, in an independent way of the distribution of temper-
ature within the product. In addition, the water migration is
considered to occur in the liquid state, and its vaporization occurs
at the surface where, therefore, happens the coupling between
mass and heat.
Some particular considerations are made in each research on
the heat and mass transfer. As examples, some interesting works
are mentioned in the following. Lima et al. (2002), describing heat
and mass transfer during drying of bananas, considered the density
multiplied by the speciﬁc heat, in the transient term of the diffu-
sion equation, as a variable quantity. Mariani et al. (2008), describ-
ing the heat transfer during drying of bananas, considered this
quantity with a constant value along time. On the other hand,
models of Lima et al. (2002) and Mariani et al. (2008) include the
energy due to heating of the vapor generated at temperature of
the surface up to drying air temperature. Although some other
works also include this energy, most researchers neglect it. A very
common simpliﬁcation is presented in the following. In the calcu-
lations, most researchers use the value of the latent heat of vapor-
ization of free water instead the value this property in the product.
Wu et al. (2004) further simpliﬁes this problem by ignoring the
latent heat of vaporization of water to describe heat transfer during
rice drying. In a literature search, the authors of the present paper
did not ﬁnd a study evaluating the implications of these simpliﬁca-
tions above mentioned. In this sense, the aim of this article is
deﬁned in the following.
Basically, this article had two distinct objectives. First, using
experimental data sets and the inverse method, a liquid diffusion
model was proposed to describe heat and mass transfer during
drying of whole bananas, determining their thermo-physical prop-
erties. For this purpose, the diffusion equation was numerically
solved, by means of the ﬁnite volume method, with a fully implicit
formulation. This solution, as well as the determination of the
thermo-physical properties, permits to simulate the migration of
both: mass and heat. The second objective of this article was to
evaluate some simpliﬁcations proposed by researchers in the
description of the heat transfer during drying.
2. Materials and methods
2.1. Drying experiments
Mature bananas Musa acuminata, subgroup Cavendish cv nanica
was acquired from the local market, Campina Grande, Brazil. The
bananas were peeled and selected by their appearance, with no
evidence of mechanical damage. The experiments were carried
out in a convective dryer with vertical ﬂux, controller of tempera-
ture and controller of air velocity (Fig. 1). One sieve (number 1)
with one whole banana was placed in the convective dryer, with
hot air at the following average temperatures: 47.9, 58.6 and
66.9 °C. In each experiment, the drying air temperature was mea-
sured twenty times along the process, and the correspondent stan-
dard deviations for the average values of 47.9, 58.6 and 66.9 °C
were 0.7, 0.8 and 0.6 °C, respectively. During the experiments,
moisture content was measured by the gravimetric method. The
bananas were weighed at time intervals ranging from 5 min at
the beginning of drying to about 4 h at the ﬁnal part of the process.
At the end of each drying, the banana was removed from the dryer
and placed within an oven at 105 °C. The product remained there
Nomenclature
Aw, Ap, Ae, B coefﬁcients of the discretized diffusion equation
a, b ﬁtting parameters
As area of the surface of the cylinder (m2
)
cp speciﬁc heat of product (J kg⟦U+0002⟧1
K⟦U+0002⟧1
)
cv speciﬁc heat of vapor of water (J kg⟦U+0002⟧1
K⟦U+0002⟧1
)
D effective moisture diffusivity (m2
s⟦U+0002⟧1
)
hm convective mass transfer coefﬁcient (m s⟦U+0002⟧1
)
hT heat transfer coefﬁcient (m s⟦U+0002⟧1
)
hH convective heat transfer coefﬁcient hH (W m⟦U+0002⟧2
K⟦U+0002⟧1
)
hfg latent heat of vaporization of water (J kg⟦U+0002⟧1
)
k thermal conductivity (W m⟦U+0002⟧1
K⟦U+0002⟧1
)
L height of cylinder (m)
M local moisture content (kgwater kg⟦U+0002⟧1
dry matter)
M average moisture content (kgwater kg⟦U+0002⟧1
dry matter)
m mass of the product
N number of control volumes
Np number of experimental points
r position inside the cylinder (m)
R radius of the cylinder (m)
R2
coefﬁcient of determination
t drying time (s)
T temperature (K)
Dr thickness of the control volumes (m)
Subscripts
0 initial
eq equilibrium
f ﬁnal
m, T moisture, thermal
w, p, e west, nodal point, east
Greek symbols
a thermal diffusivity (m2
s⟦U+0002⟧1
)
v2
chi-square
CU
transport coefﬁcient (dimension depends on the process
under study)
U dependent variable of the diffusion equation (dimen-
sion depends on the phenomenon under study)
k transport coefﬁcient (dimension depends on the phe-
nomenon under study)
q density (kg m⟦U+0002⟧3
)
ri standard deviation of the experimental moisture con-
tent at the point i
Fig. 1. Convective dryer: (a) Cross-section; (b) positions of the trays on the cross-
section: number 1 – banana for mass measurement and number 2 – banana with
thermocouple for temperature measurement.
66 W.P. da Silva et al. / Journal of Food Engineering 141 (2014) 65–73
```

## PDF 第 3 页

```text
for 24 h, enabling the measurement of the dry matter. The average
drying air temperatures, dimensions, moisture contents, dry mat-
ters and speciﬁc heats of the vapor are given in Table 1.
Information about the drying air (average relative humidity, RH,
and velocity, ⟦U+0016⟧
v) and the room air (average temperature and relative
humidity) is given in Table 2 for each drying air temperature. The
relative humidity, velocity of the air drying as well as room tem-
perature was measured twenty times along of each experiment,
and the values provided in Table 2 are the average values obtained
in each measurement process.
The radius R and height L was measured every instant in which
the bananas were removed from the dryer to measure the mass.
This way, the ratio between the current and initial radius, R/R0,
was determined at every instant. Expressions R/R0 as a function
of the average moisture content M were obtained using curve ﬁt-
ting for all drying air temperatures, as is shown in Table 3.
If the expressions R/R0 (Table 3) are drawn as a function of the
average moisture content for all drying air temperatures in a same
system of axes, the obtained lines are very close one of each other.
On the other hand, the measurements of mass, radius and height
enabled to determine the density of the bananas along the drying
process. Thus, it is possible to determine an expression for the den-
sity of the bananas as a function of the moisture content of the
product.
A thermocouple was placed in the center of a second banana
(sieve number 2), which was also placed in the dryer. The initial
temperature of the banana is the room temperature, which is pro-
vided in Table 2. For each drying air temperature T, care was exer-
cised to select two bananas with the same dimensions (or very
close) to minimize size effect on the experimental data. The data-
sets of temperature were collected in regular time interval by using
a digital Multimeter Cole Parmer, with temperature range of ⟦U+0002⟧180°
to 370 °C; and accuracy of 0.1 °C in the temperature range of
interest.
2.2. One-dimensional diffusion equation and its discretization
In order to describe the processes involved during drying, the
following assumptions were considered: (1) the product was
considered homogeneous and isotropic; (2) the water migration
can be described by liquid diffusion model; (3) the mass migration
is considered under isothermal conditions, since at initial instants
of drying, the thermal diffusivity (10⟦U+0002⟧7
m2
s⟦U+0002⟧1
) is greater than the
moisture diffusivity (10⟦U+0002⟧10
m2
s⟦U+0002⟧1
) and, consequently, the Biot
number for heat transfer is lesser than the mass transfer Biot
number; (4) the mass and thermal diffusivities are variable
properties; (5) the coupling between mass and heat occurs at sur-
face, where the liquid phase is transformed to vapor. In addition to
these assumptions, it was established that radial shrinkage must
be included to model.
For a cylinder of radius R and height L, in which L ⟦U+0003⟧ R, the one-
dimensional diffusion equation can be written in the following
way:
@ðkUÞ
@t
¼
1
r
@
@r
rCU @U
@r
⟦U+0002⟧ ⟦U+0003⟧
ð1Þ
where U is the variable that describes a diffusive process (its unit
depends on the speciﬁc process); t is the time (s); r deﬁnes the
radial position within the cylinder (m); k and CU
are the properties
of the product (their units depend on the speciﬁc process). In order
to numerically solve Eq. (1) using the ﬁnite volume method with
fully implicit formulation (Patankar, 1980), the domain was divided
into N control volumes, generating a uniform grid in the circular
section of the cylinder, as is shown in Fig. 2a.
Fig. 2b shows details of an internal control volume P and its
neighbors to west (W) and east (E). Integrating Eq. (1) on space,
2prPDrL, and time, from t to t + Dt, the following result is obtained:
kpUP ⟦U+0002⟧ k0
pU0
P
Dt
rpDr ¼ reCU
e
@U
@r
⟦U+0004⟧
⟦U+0004⟧
⟦U+0004⟧
⟦U+0004⟧
e
⟦U+0002⟧ rwCU
w
@U
@r
⟦U+0004⟧
⟦U+0004⟧
⟦U+0004⟧
⟦U+0004⟧
w
ð2Þ
in which the subscripts p, e and w represent nodal point; interface
east and interface west, respectively. The term with superscript 0 is
Table 1
Temperature, dimension, moisture content, dry matter and speciﬁc heat of vapor for each drying air temperature.
Tair (°C) L0 (mm) R0 (mm) M0 (db) Mf (db) Meq (db) md (kg) cv (J kg⟦U+0002⟧1
°C⟦U+0002⟧1
)
47.9 141 14.9 3.43 0.202 0.121 0.0192 1908
58.6 143 14.8 3.14 0.224 0.108 0.0223 1911
66.9 165 15.3 2.90 0.228 0.094 0.0276 1914
Table 2
Relative humidity, velocity and temperature.
Drying air Room air
T (°C) RH (%) ⟦U+0016⟧
v (m/s) T0 (°C) RHroom (%)
47.9 20.3 1.84 25.3 59.3
58.6 10.4 1.70 25.6 48.3
66.9 6.6 1.50 24.6 48.4
Table 3
Ratio R/R0 as a function of the average moisture
content.
T (°C) R/R0
47.9 ð0:2500M þ 0:1576Þ
1=3
58.6 ð0:2821M þ 0:1123Þ
1=3
66.9 ð0:3016M þ 0:1160Þ
1=3
Fig. 2. (a) Uniform grid in the circular section of the inﬁnite cylinder highlighting
an internal control volume with nodal point P; (b) details of the control volume P
and its neighbors to west (W) and east (E).
W.P. da Silva et al. / Journal of Food Engineering 141 (2014) 65–73 67
```

## PDF 第 4 页

```text
calculated at beginning of the time interval (t), while the terms
without this superscript are calculated at the end (t + Dt). Eq. (2)
is a partial result that will be used to obtain algebraic equations
for each type of control volume as is shown in the following.
2.2.1. Internal control volumes
For this type of control volume, with neighbors to west and east,
the derivatives of Eq. (2) can be given in the following way:
@U
@r
⟦U+0004⟧
⟦U+0004⟧
⟦U+0004⟧
⟦U+0004⟧
e
ﬃ
UE ⟦U+0002⟧ UP
Dr
@U
@r
⟦U+0004⟧
⟦U+0004⟧
⟦U+0004⟧
⟦U+0004⟧
w
ﬃ
UP ⟦U+0002⟧ UW
Dr
ð3a—bÞ
Substituting Eq. (3a–b) into Eq. (2), the following algebraic
equation is obtained:
ApUP þ AwUW þ AeUE ¼ B ð4Þ
in which
Aw ¼ ⟦U+0002⟧
rw
Dr
CU
w
kP
Ap ¼
rPDr
Dt
þ
re
Dr
CU
e
kP
þ
rw
Dr
CU
w
kP
Ae ¼ ⟦U+0002⟧
re
Dr
CU
e
kP
B ¼
k0
PrPDr
kPDt
U0
P
ð5a—dÞ
2.2.2. Control volume number 1
For the control volume at the center of the grid, due to the sym-
metry, the west mass ﬂux is zero. Consequently, the derivative
given in Eq. (3b) is zero. Thus, for control volume number 1 it is
obtained:
ApUP þ AeUE ¼ B ð6Þ
where
Ap ¼
rPDr
Dt
þ
re
Dr
CU
e
kP
Ae ¼ ⟦U+0002⟧
re
Dr
CU
e
kP
B ¼
k0
PrPDr
kPDt
U0
P ð7a—cÞ
2.2.3. Water removal and heat transport
In order to apply the above results in the water removal, in Eq.
(1) it should be imposed: U ⟦U+0005⟧ M, in which M is the moisture con-
tent in dry basis (kgwater kg⟦U+0002⟧1
dry matter); k = 1 (dimensionless); CU
= D,
i.e., effective moisture diffusivity (m2
s⟦U+0002⟧1
).
As an observation, in order to describe heat transport, the ther-
mal properties referring to advection, radiation, phase change, heat
sources and conduction should be known. Many times, solely the
conduction mechanism and phase change are used to describe heat
transfer and, consequently, the properties involved (such as ther-
mal diffusivity and conductivity) are considered as ‘‘apparent’’.
However, in this article, for simplicity, the thermal diffusivity will
continue to be named with this same name.
In the heat conduction study, the imposition on the variables of
Eq. (1) U, k and CU
are as follows: U ⟦U+0005⟧ T, i.e., temperature (K);
k ¼ qcp, where q is the density (kg m⟦U+0002⟧3
) and cp is the speciﬁc heat
of the product (J kg⟦U+0002⟧1
K⟦U+0002⟧1
); CU
= k, i.e., thermal conductivity
(W m⟦U+0002⟧1
K⟦U+0002⟧1
). If the thermal conductivity is divided by qcp, a thermal
property called thermal diffusivity (m2
s⟦U+0002⟧1
) is obtained: a = k/qcp.
For the control volume N, which is in contact with the external
medium, two different equations must be obtained to complete the
discretization of the diffusion equation to describe mass and heat
transfer. These equations are obtained in the following.
2.2.4. Water removal: control volume N at boundary of the cylinder
For the control volume N, supposing boundary condition of the
third kind, the following discretized equation is obtained:
ApMP þ AwMW ¼ B ð8Þ
where
Ap ¼
rPDr
Dt
þ
reDe
De
hm
þ Dr
2
þ
rw
Dr
Dw Aw ¼ ⟦U+0002⟧
rw
Dr
Dw B ¼
rPDr
Dt
M0
P þ
reDe
De
hm
þ Dr
2
Meq
ð9a—cÞ
in which hm is the convective mass transfer coefﬁcient (m s⟦U+0002⟧1
) and
Meq is the equilibrium moisture content (db). Detailed steps on the
obtaining of Eq. (9a–c) for moisture migration are presented by
Silva et al. (2012a).
2.2.5. Heat transport: control volume N at boundary of the cylinder
In this article, apparent liquid diffusion was assumed. Thus,
liquid water migrates from internal medium to the surface of the
product, where occurs change to vapor. Thus, for the control vol-
ume N, the boundary condition of the third kind is expressed in
the following way:
⟦U+0002⟧ae
@T
@r
⟦U+0004⟧
⟦U+0004⟧
⟦U+0004⟧
⟦U+0004⟧
e
¼ hT ðTe ⟦U+0002⟧ TeqÞ ⟦U+0002⟧
½hfg þ cvðTe ⟦U+0002⟧ TeqÞ⟦U+0006⟧ dm
dt
qcPAs
ð10Þ
where hT is the heat transfer coefﬁcient (m s⟦U+0002⟧1
); Teq is the equilib-
rium temperature (K); cv is speciﬁc heat of the vapor (J kg⟦U+0002⟧1
K⟦U+0002⟧1
);
hfg is the latent heat of vaporization (J kg⟦U+0002⟧1
); dm/dt is the water loss
rate (kg s⟦U+0002⟧1
) and As is the area of the surface of the cylinder (m2
),
given by As = 2pRL. In this article, it was assumed that the ratios
L/L0 are given by the same expressions provided in Table 3 for the
radius. The convective heat transfer coefﬁcient hH (W m⟦U+0002⟧2
K⟦U+0002⟧1
) is
related with hT through the expression hT = hH/(qcp). On the other
hand, combining the result to be obtained with the discretization
of Eq. (10) with Eq. (2) applied to heat transfer, Eq. (11) is
determined:
ApTP þ AwTW ¼ B ð11Þ
in which
Ap ¼
rPDr
Dt
þ
aere
ae
hT ⟦U+0002⟧ cv
qcpAs
dm
dt
þ Dr
2
þ
rw
Dr
aw Aw ¼ ⟦U+0002⟧
rw
Dr
aw
B ¼
q0
c0
PrPDr
qcpDt
T0
P þ
aere
ae
hT ⟦U+0002⟧
cv
qcpAs
dm
dt
þ Dr
2
Teq þ
aere
hfg
qcP As
dm
dt
ae þ Dr
2
hT ⟦U+0002⟧ cv
qcpAs
dm
dt
⟦U+0005⟧ ⟦U+0006⟧
ð12a—cÞ
2.3. Mass and thermal diffusivity
For the nodal points, the diffusivity CU
(D or a) can be calcu-
lated from an appropriate relation between such property and
the value of U,
CU
¼ fða; b; UÞ ð13Þ
where a and b are parameters that ﬁt the numerical solution to the
experimental data, and they can be determined by optimization.
On the interfaces of the internal control volumes, for example e,
for uniform grids the following expression (harmonic mean)
should be used to determine CU
(Patankar, 1980):
CU
e ¼
2CU
E CU
P
CU
E þ CU
P
; ð14Þ
If the diffusivity is constant, the coefﬁcients A of the discretized
equations are calculated only once, and B is calculated in each time
step because its value depends on U0
P, which is the value of U in the
control volume P at the initial instant of each time step. On the
other hand, if CU
is variable, the coefﬁcients A are also calculated
in each time step, due to the nonlinearities caused by the variation
of such parameter. In this case, if the time reﬁnement is adequate,
errors due to the nonlinearities can be discarded.
68 W.P. da Silva et al. / Journal of Food Engineering 141 (2014) 65–73
```

## PDF 第 5 页

```text
In this article, the function f(a,b,M) used to relate the effective
mass diffusivity with the local value of the moisture content is
given by (Silva et al., 2012a):
D ¼ bm expðamMÞ; ð15Þ
where am and bm are parameters to be determined by optimization
and M is the local moisture content in dry basis.
It is well known that the thermal diffusivity of a product
depends on its composition. In this sense, the thermal diffusivity
of fresh fruits is very high, due to their high moisture content. Dur-
ing drying, the thermal diffusivity of a fruit at any instant depends
on its water quantity. As water is continually lost during drying,
i.e., the moisture content of the product is diminishing, the value
of the thermal diffusivity also diminishes along time (Lima et al.,
2002; Mariani et al., 2008). Thus, in this article, for each drying
air temperature, the following expression was proposed for this
property:
a ¼ bT expðaT M2
Þ; ð16Þ
in which aT and bT are constants for each drying air temperature,
and are determined by optimization. On the other hand, M is the
average moisture content of the fruit at any instant during the
drying process.
2.4. General considerations
The water loss rate, dm/dt, necessary to describe heat transport,
can be determined when water migration is described. Thus, ini-
tially water migration was studied. In each time step, a system of
equations (Eqs. (4), (6), and (8)) is solved using Tridiagonal Matrix
Algorithm method, TDMA (Press et al., 1996). Since water migra-
tion is described, in each time step the water loss rate is deter-
mined by:
dm
dt
¼
mðt þ DtÞ ⟦U+0002⟧ mðtÞ
Dt
ð17Þ
in which the mass of water (kg) at instant t is given by
mðtÞ ¼ mdMðtÞ where md is the mass of the dry matter (kg), given
in Table 1, and MðtÞ is the average moisture content in dry basis
(kgwater kg⟦U+0002⟧1
dry matter), calculated by:
MðtÞ ¼
PN
i¼1Miri
PN
i¼1ri
ð18Þ
where Mi is the moisture content in the control volume ‘‘i’’ and ri is
its radius (m). Due to the shrinkage, in each time step the radius of
the cylinder varies and, therefore, its value must be recalculated, as
well as the thickness Dr of the control volumes of the uniform grid.
Expressions for these calculations are given in Table 3.
The latent heat of water vaporization at the surface of the bana-
nas was calculated according to the expression provided by Silva
et al. (2012b):
hfg ¼ 2529:1Mð⟦U+0002⟧1:782⟦U+0007⟧10⟦U+0002⟧2
⟦U+0002⟧3:570⟦U+0007⟧10⟦U+0002⟧4
TÞ
⟦U+0002⟧ 2:386T ð19Þ
where hfg is obtained in kJ kg⟦U+0002⟧1
when M is given in dry basis and T in
°C.
For a given time step, in order to use Eqs. (4), (6), and (11) to
determine the temperature in each control volume, the speciﬁc
heat and density must be known at beginning and ﬁnal of each
time step. This is obvious because the coefﬁcients B of these equa-
tions depend on these values. The speciﬁc heat of the bananas was
estimated according to the expression provided by Sweat (1986)
for agricultural products:
cp ¼ 1381 þ 2930X ð20Þ
where X is the average moisture content, in wet basis (decimal), and
cp is obtained in J kg⟦U+0002⟧1
K⟦U+0002⟧1
.
Speciﬁc heat for the water vapor, cv, is provided in Table 1. On
the other hand, with the measurements accomplished in the
experiments, it was possible to determine an expression for the
density q of the bananas (kg m⟦U+0002⟧3
) as a function of the average
moisture content, M (db), by curve ﬁt:
q ¼ 1533e⟦U+0002⟧0:1704M
ð21Þ
Thus, in each time step, if the values of the thermal diffusivity
and heat transfer coefﬁcient are provided in Eqs. (4), (6), and
(11), the obtained system can be solved to determine the temper-
ature in each control volume. At each time step, the system of
equations was solved by using of TDMA method. Similar comment
is also valid to study mass migration. Note that, if the thermal dif-
fusivity and heat transfer coefﬁcient are unknown, the parameters
aT, bT and hT can be determined by optimization (inverse method)
using experimental data set, as is presented in the following.
2.5. Optimization
In order to determine the parameters CU
(D or a) and h (hm or
hT), the parameters a and b of the function CU
= f(a, b, U) and h can
be determined by optimization using an experimental dataset. The
expression of the chi-square (Bevington and Robinson, 1992;
Taylor, 1997) was chosen as objective function:
v2
¼
X
Np
j¼1
Uexp
j ⟦U+0002⟧ Usim
j
h i2 1
r2
j
ð22Þ
where Uexp
j is the value of U measured in the experimental point
‘‘j’’; Usim
j is the correspondent average value of U obtained by simu-
lation; Np is the number of experimental points and 1=r2
j is the sta-
tistical weight referring to the point ‘‘j’’. If the statistical weights are
unknown, they can be made equal to a common value, for instance
1. In Eq. (22), the chi-square depends on Usim
j , which depends on CU
(i.e., parameters am or aT and bm or bT) and h (hm or hT). Thus, the
parameters a, b and h can be determined by minimization of Eq.
(22) through successive trials.
3. Results and discussion
The circular section of the bananas was divided into 100 control
volumes and the drying time was divided into 5000 steps. An unre-
ported study on grid and time reﬁnement indicated that such val-
ues are adequate to describe two processes: mass and heat
transfer.
3.1. Results for water migration
The effective moisture diffusivity was considered variable as a
function of the local moisture content as is given by Eq. (15), and
the radius was also considered variable, according to Table 3. Thus,
the parameters related with water transfer, obtained by optimiza-
tion, are presented in Table 4.
The simulations of the drying kinetics are shown in Fig. 3a–c,
and the superposition of these simulations is shown in Fig. 3d.
As additional information, the graphs of Fig. 3a–c were gener-
ated by own software developed to perform the optimizations.
Table 4
Parameters of the water migration obtained by optimization.
T (°C) am bm (m2
min⟦U+0002⟧1
) hm (m min⟦U+0002⟧1
) R2
v2
47.9 0.687 15.4 ⟦U+0007⟧ 10⟦U+0002⟧9
2.66 ⟦U+0007⟧ 10⟦U+0002⟧5
0.99970 15.6 ⟦U+0007⟧ 10⟦U+0002⟧3
58.6 0.785 19.4 ⟦U+0007⟧ 10⟦U+0002⟧9
2.68 ⟦U+0007⟧ 10⟦U+0002⟧5
0.99989 3.87 ⟦U+0007⟧ 10⟦U+0002⟧3
66.9 0.821 28.9 ⟦U+0007⟧ 10⟦U+0002⟧9
2.99 ⟦U+0007⟧ 10⟦U+0002⟧5
0.99964 9.20 ⟦U+0007⟧ 10⟦U+0002⟧3
W.P. da Silva et al. / Journal of Food Engineering 141 (2014) 65–73 69
```

## PDF 第 6 页

```text
On the other hand, with the results from Table 4, the graphs of the
functions D(M), given by Eq. (15), are presented in Fig. 4 for three
temperatures of the drying air.
In order to present the moisture distributions within the circu-
lar section that represents the bananas, Fig. 5 highlights these dis-
tributions at 200 min, for three temperatures of the drying air.
3.2. Results for heat transport
Thermal diffusivity was considered variable as a function of the
average moisture content, as is given by Eq. (16). In the heat trans-
port study, the radius was also considered variable, according to
Table 3. Thus, the parameters related with the heat transfer,
obtained by optimization, are presented in Table 5.
The simulations of the heating kinetics in the center of the
bananas are shown in Fig. 6a–c, while Fig. 6d presents the superpo-
sition of these simulations.
Note that the graphs of Fig. 6a–c were also generated by soft-
ware developed to perform the optimization processes.
With the results from Table 5, the graphs of the functions aðMÞ,
given by Eq. (16), are presented in Fig. 7, for three temperatures of
the drying air.
The distributions of temperature within the circular section that
represents the bananas at t = 10 min are given in Fig. 8 for three
temperatures of the drying air.
3.3. Analysis of simpliﬁcations for the heat transfer problem
3.3.1. Exclusion of the heating of the vapor
In the proposed model, vapor is generated at temperature of the
surface and is heated to the drying air temperature. In order to test
the inﬂuence of the heating of the vapor, a simulation was
Fig. 3. Simulation of water migration at drying air temperature of: (a) 47.9 °C; (b)
58.6 °C; (c) 66.9 °C; (d) superposition of the simulated curves.
Fig. 4. Effective moisture diffusivity as a function of the local moisture content at
temperature of: (a) 47.9 °C; (b) 58.6 °C; (c) 66.9 °C.
Fig. 5. Distribution of the moisture content at t = 200 min for the drying air
temperature of: (a) 47.9 °C; (b) 58.6 °C; (c) 66.9 °C.
Table 5
Parameters of the heat conduction obtained by optimization.
T (°C) aT bT (m2
min⟦U+0002⟧1
) hT (m min⟦U+0002⟧1
) R2
v2
47.9 0.313 1.26 ⟦U+0007⟧ 10⟦U+0002⟧7
5.61 ⟦U+0007⟧ 10⟦U+0002⟧4
0.99071 14.3
58.6 0.398 1.06 ⟦U+0007⟧ 10⟦U+0002⟧7
5.71 ⟦U+0007⟧ 10⟦U+0002⟧4
0.98843 28.9
66.9 0.520 1.26 ⟦U+0007⟧ 10⟦U+0002⟧7
9.49 ⟦U+0007⟧ 10⟦U+0002⟧4
0.98084 33.4
70 W.P. da Silva et al. / Journal of Food Engineering 141 (2014) 65–73
```

## PDF 第 7 页

```text
performed at 58.6 °C, considering the parameters given in Table 5,
but supposing cv = 0. In this case, the statistical indicators of the
simulation were v2
= 29.2 (instead 28.9) and R2
= 0.98835 (instead
0.98843). A graph showing the simulation of the heating kinetics at
the center of the banana does not present a signiﬁcant visual differ-
ence when compared with Fig. 6b and, therefore, was not pre-
sented herein. Similar results were obtained for the drying air
temperatures of 47.9 and 66.9 °C.
3.3.2. Latent heat of water vaporization
In a simulation with the drying air temperature at 58.6 °C, if the
results obtained in Table 5 are used, but latent heat of water vapor-
ization is neglected (hfg = 0), the statistical indicators are:
v2
= 4146.1 (instead 28.9) and R2
= 0.75502 (instead 0.98843).
These results are completely unacceptable, and similar results
are obtained for the drying air temperatures of 47.9 and 66.9 °C.
On the other hand, at 58.6 °C, the use of the value of the latent heat
of vaporization of free water in the simulation resulted in statisti-
cal indicators given by v2
= 29.6 (instead 28.9) and R2
= 0.98832
(instead 0.98843). Similar results were obtained at 47.9 and
66.9 °C.
3.3.3. Constant density and speciﬁc heat of bananas
In many occasions, the transient term of Eq. (1) applied to heat
transfer, given by @(qcpT)/@t, is written as qcp@T/@t, i.e., in this term
the product qcp is considered constant. In order to test this simpli-
ﬁcation for the drying case, the results obtained in Table 5 for
T = 58.6 °C were used in a simulation, considering the transient
term given by qcp@T/@t. As result, the chi-square was 264.1
(instead 28.9) and the determination coefﬁcient was 0.97835
(instead 0.98843). Similar results were also obtained for the drying
air temperatures of 47.9 and 66.9 °C, indicating that this simpliﬁca-
tion should be avoided in drying studies.
3.4. Discussion
Basically, in the transient diffusion study, two methods are used
to determine the thermal diffusivity and heat transfer coefﬁcient of
agricultural products: empirical correlations (Karim and Hawlader,
2005; Perussello et al., 2013) and optimization (Lima et al., 2002;
Fig. 6. Temperature in the center of the banana at drying air temperature of: (a)
47.9 °C; (b) 58.6 °C; (c) 66.9 °C; (d) superposition of the simulated curves.
Fig. 7. Thermal diffusivity as a function of the average moisture content at drying
air temperature of: (a) 47.9 °C; (b) 58.6 °C; (c) 66.9 °C.
Fig. 8. Distribution of the temperatures at t = 10 min for the drying air temperature
of: (a) 47.9 °C; (b) 58.6 °C; (c) 66.9 °C.
W.P. da Silva et al. / Journal of Food Engineering 141 (2014) 65–73 71
```

## PDF 第 8 页

```text
Silva et al., 2011, 2013). In the present article, only optimizations
were used to determine a and hT, and the obtained results are com-
patible with those reported in the literature for bananas (Lima
et al., 2002; Mariani et al., 2008).
Trough an inspection of Table 4 it is possible to afﬁrm that the
statistical indicators to describe the mass transfer are excellent.
Particularly, the determination coefﬁcients are greater than
0.99960. Similar conclusion on the adequacy of the proposed model
can be obtained by an observation of Fig. 3a–c for three tempera-
tures of the drying air. On the other hand, Fig. 3d presents a superpo-
sition of the drying kinetics, in which it is possible to evaluate how
much one simulation is faster than other. From Table 4 and
Eq. (15), the minimum and maximum values of the effective mois-
ture diffusivity are 2.79 ⟦U+0007⟧ 10⟦U+0002⟧10
m2
s⟦U+0002⟧1
(47.9 °C and M = 0.121 db)
and 5.21 ⟦U+0007⟧ 10⟦U+0002⟧9
m2
s⟦U+0002⟧1
(66.9 °C and M = 2.90 db). Details on
effective moisture diffusivity as a function of the local moisture
content are presented in Fig. 4. In this ﬁgure it is realized that, the
more the temperature of the drying air is high, the greater the
effective moisture diffusivity. This obtained result is a consequence
of the following fact: increasing the drying air temperature increases
the overall product temperature and, hence, the moisture diffusiv-
ity. On the other hand, the convective mass transfer coefﬁcient
varied from 4.43 ⟦U+0007⟧ 10⟦U+0002⟧7
to 4.98 ⟦U+0007⟧ 10⟦U+0002⟧7
m s⟦U+0002⟧1
. Similar results were
obtained by Silva et al. (2012a) and Lima et al. (2002) studying
drying of bananas.
The moisture distributions are presented in Fig. 5, with no scale,
for three drying air temperatures, at t = 200 min. An observation of
this ﬁgure allows to conclude that the more the temperature of the
drying air is high, the greater the loss of moisture. Although this
conclusion is quite obvious, the calculations performed herein
are necessary for a subsequent determining the stress within the
fruit due to the difference in the moisture concentration.
Table 5 presents the results of the optimizations for the temper-
atures measured in the center of the bananas. The statistical indica-
tors show that the obtained results are reasonable. Particularly, the
determination coefﬁcients are greater than 0.98000. A visual obser-
vation of Fig. 6a–c makes it possible to conclude that the simulated
lines agree with experimental datasets. On the other hand, Fig. 6d
enables to realize that the heating process is very fast. Differently
of water migration, few minutes are enough so that the temperature
at center of the fruit approximates of its equilibrium value. This fact
permitted to establish the assumption number 3 of this article: ‘‘the
mass migration is considered under isothermal conditions, since at
initial instants of drying the thermal diffusivity (10⟦U+0002⟧7
m2
s⟦U+0002⟧1
) is
greater than the moisture diffusivity (10⟦U+0002⟧10
m2
s⟦U+0002⟧1
)’’.
Inspection of Fig. 7 indicates that, for all temperatures of the
drying air, the thermal diffusivity exponentially decreases with
the decreasing of average moisture content of the banana.
Shyamal et al. (1994), studying the thermal properties of the
wheat, concluded that the thermal diffusivity decrease linearly
with moisture content. However, the range of the moisture content
in drying of grains is lesser than the range of fruits such as bananas.
A similar result to the obtained herein for thermal diffusivity of
bananas was obtained by Mariani et al. (2008). However, the
expressions proposed by these researchers for the thermal diffusiv-
ity involved three and four parameters and, in the present article,
only two parameters were involved. In the present article, at the
beginning of drying, the values for the thermal diffusivities are
given by 0.835 ⟦U+0007⟧ 10⟦U+0002⟧7
(47.9 °C), 0.894 ⟦U+0007⟧ 10⟦U+0002⟧7
(58.6 °C) and
1.67 ⟦U+0007⟧ 10⟦U+0002⟧7
m2
s⟦U+0002⟧1
(66.9 °C). Based on the literature, these results
are acceptable for agricultural products with high moisture con-
tent, such as bananas. At the end of the drying processes, the values
obtained in this work for thermal diffusivity are of about
2.0 ⟦U+0007⟧ 10⟦U+0002⟧9
m2
s⟦U+0002⟧1
. The highest value obtained in the present paper
for the thermal diffusivity (1.67 ⟦U+0007⟧ 10⟦U+0002⟧7
m2
s⟦U+0002⟧1
) is lower that those
obtained by Mariani et al. (2008), 1.88 ⟦U+0007⟧ 10⟦U+0002⟧7
, and Lima et al.
(2002), 2.70 ⟦U+0007⟧ 10⟦U+0002⟧7
m2
s⟦U+0002⟧1
. On the other hand, the value obtained
herein is closest to the value of the thermal diffusivity of the water,
as is expected. In addition, the lower value obtained in this article,
at the end of drying, is compatible with two works above-
mentioned.
In their article, Mariani et al. (2008) have determined the values
for convective heat transfer coefﬁcient based on the Nusselt num-
ber, i.e., using empirical correlations instead optimization. Their
results were from 15 to 35 W m⟦U+0002⟧2
°C⟦U+0002⟧1
. In the present work, this
property was determined by optimization and, at beginning of
the process, ranged between 15.2 (47.9 °C) and 28.3 W m⟦U+0002⟧2
°C⟦U+0002⟧1
(66.9 °C⟦U+0002⟧1
). These results are compatible with those from Mariani
et al. (2008), and also agree with those obtained by Lima et al.
(2002): from 12.7 to 19.0 W m⟦U+0002⟧2
°C⟦U+0002⟧1
.
From Fig. 8 it is possible to realize that, at instant t = 10 min, the
range of temperature in the interior of the banana increases with
the increasing of the drying air temperature. Remembering that
bananas are at room temperature at the initial instant, at drying
air temperature of 47.9 °C and t = 10 min the range of temperature
in the circular section was from 26.2 (center) to 28.9 °C (surface).
For the drying air temperatures of 58.6 and 66.9 °C, these ranges
were 28.4–34.0 and 37.3–46.4 °C, respectively. Finally, although
the three circles of Fig. 8 have the same size, i.e., three ﬁgures
are drawn with no scale, it is expected that the circle related to
drying at 66.9 °C has lesser radius than other circles, once the
banana at this temperature dries faster than the other two cases.
Obviously, the shrinkage due to water loss is more important than
the effect of expansion by temperature increase.
Lima et al. (2002) and Mariani et al. (2008), in their analyses,
included the speciﬁc heat of the water vapor in order to describe
heat transport. However, several researchers such as Rinaldi et al.
(2011) and also Ramsaroop and Persad (2012), studying simulta-
neous heat and mass transfer, did not consider this phenomenon.
The simulations performed in the present work made it possible
to realize that the heating of vapor at surface temperature to dry-
ing air temperature is not signiﬁcant in the description of the heat
transport during convective drying of bananas. On the other hand,
Wu et al. (2004) studied heat and mass transfer during drying of
rice. These researchers used two diffusion equations to describe
water and heat migration, supposing that two phenomena are
independent, i.e., the latent heat of water vaporization was
neglected. However, the results obtained in the present article
indicated that the coupling between two phenomena is very
important and the latent heat of water vaporization cannot be
neglected. Another simulation performed in the present article
has shown that the use of the latent heat of vaporization of free
water (instead latent heat of vaporization of water in the product)
is not signiﬁcant to describe drying of bananas.
Many times the product qcp in the transient term is considered
constant in the equation of heat conduction (Mariani et al., 2008;
Ramsaroop and Persad, 2012; Lemus-Mondaca et al., 2013). This
consideration made it possible to determine an analytical solution
for the equation of heat conduction in a hemispherical shell geom-
etry (Ramsaroop and Persad, 2012). However, the results obtained
in the present paper indicated that such consideration worsened
the results of model proposed and, consequently, should be
avoided.
4. Conclusion
Liquid diffusion model, with vaporization of water at surface of
the bananas, was assumed in this article. Model included mass and
thermal diffusivities as variable properties, boundary conditions of
the third kind, and also included the shrinkage. Using an inﬁnite
cylinder to represent the bananas, this model well described the
mass and heat transfer during the drying process.
72 W.P. da Silva et al. / Journal of Food Engineering 141 (2014) 65–73
```

## PDF 第 9 页

```text
In the description of mass migration, the determination coefﬁ-
cients were greater than 0.99960 for all drying air temperatures.
Also, it can be concluded that the expressions obtained for D(M),
as well as the values for convective mass transfer coefﬁcients are
adequate to describe mass migration during drying of bananas.
On the other hand, in the description of heat transport, the deter-
mination coefﬁcients were greater than 0.98000. In addition, the
values obtained for thermal diffusivity and convective heat trans-
fer coefﬁcient are compatible with the expected values for mature
bananas submitted to the experiments performed. Thus, it can be
concluded that the expressions obtained for aðMÞ as well as the
values for convective heat transfer coefﬁcients are adequate to
describe heat transport during drying.
It was possible to realize that the exclusion of the energy used
to heat the vapor from the surface temperature up to the drying air
temperature does not inﬂuence the description of the heating of
bananas in a signiﬁcant way. However, the exclusion of latent heat
of vaporization strongly worsened the obtained results. On the
other hand, the use of the value of the latent heat of vaporization
of free water in the simulations (instead latent heat of vaporization
of water in the product) is not signiﬁcant to describe the process.
Finally, it was concluded that the consideration of the product
qcp with a constant value in the equation of heat conduction
should be avoided.
Acknowledgment
The ﬁrst author would like to thank CNPq (Conselho Nacional
de Desenvolvimento Cientíﬁco e Tecnológico) for the support given
to this work and for his research grant (Process Number 301697/
2012-4).
References
Bevington, P.R., Robinson, D.K., 1992. Data Reduction and Error Analysis for the
Physical Sciences, second ed. WCB/McGraw-Hill, Boston.
Da Silva, W.P., Silva, C.M.D.P.S., Lins, M.A.A., 2011. Determination of expressions for
the thermal diffusivity of canned foodstuffs by the inverse method and
numerical simulations of heat penetration. Int. J. Food Sci. Technol. 46 (4),
811–818.
Karim, M.A., Hawlader, M.N.A., 2005. Drying characteristics of banana: theoretical
modelling and experimental validation. J. Food Eng. 70 (1), 35–45.
Lemus-Mondaca, R.A., Zambra, C.E., Vega-Gálvez, A., Moraga, N.O., 2013. Coupled
3D heat and mass transfer model for numerical analysis of drying process in
papaya slices. J. Food Eng. 116 (1), 109–117.
Lima, A.G.B., Queiroz, M.R., Nebra, S.A., 2002. Heat and mass transfer model
including shrinkage applied to ellipsoidal products: case study for drying of
bananas. Asia-Pacif. J. Chem. Eng. 10 (3–4), 281–304.
Mariani, V.C., Lima, A.G.B., Coelho, L.S., 2008. Apparent thermal diffusivity
estimation of the banana during drying using inverse method. J. Food Eng. 85
(4), 569–579.
Patankar, S.V., 1980. Numerical Heat Transfer and Fluid Flow. Hemisphere
Publishing Corporation, New York.
Perussello, C.A., Kumar, C., de Castilhos, F., Karim, M.A., 2013. Heat and mass
transfer modeling of the osmo-convective drying of yacon roots (Smallanthus
sonchifolius). Appl. Therm. Eng. 63 (1), 23–32.
Press, W.H., Teukolsky, S.A., Vetterling, W.T., Flannery, B.P., 1996. Numerical Recipes
in Fortran 77. The Art of Scientiﬁc Computing, vol. 1. Cambridge University
Press, New York.
Ramsaroop, R., Persad, P., 2012. Determination of the heat transfer coefﬁcient and
thermal conductivity for coconut kernels using an inverse method with a
developed hemispherical shell model. J. Food Eng. 110 (1), 141–157.
Rinaldi, M., Chiavaro, E., Gozzi, Massini, E.R., 2011. Simulation and experimental
validation of simultaneous heat and mass transfer for cooking process of
Mortadella Bologna PGI. Int. J. Food Sci. Technol. 46 (3), 586–593.
Shyamal, D.K., Chakraverty, A., Banerjee, H.D., 1994. Thermal properties of raw,
parboiled and debranned parboiled wheat and wheat bulgur. Energy Convers.
Manage. 35 (9), 801–804.
Silva, W.P., Silva, C.M.D.P.S., Nascimento, P.L., Carmo, J.E.F., Silva, D.D.P.S., 2011.
Inﬂuence of the geometry on the numerical simulation of the cooling kinetics of
cucumbers. Spanish J. Agric. Res. 9 (1), 242–251.
Silva, W.P., Silva, C.M.D.P.S., Farias, V.S.O., Gomes, J.P., 2012a. Diffusion models to
describe the drying process of peeled bananas: optimization and simulation.
Drying Technol. 30 (1), 164–174.
Silva, W.P., Silva, C.M.D.P.S., Gama, F.J.A., Gomes, J.P., 2012b. An empiric equation for
the latent heat of vaporization of moisture in bananas during its isothermal
drying. Agric. Sci. 3 (2), 214–220.
Silva, W.P., Silva, C.M.D.P.S., Gomes, J.P., 2013. Drying description of cylindrical
pieces of bananas in different temperatures using diffusion models. J. Food Eng.
117 (3), 417–424.
Sweat, V.E., 1986. Thermal properties of foods. In: Rao, M.A., Rizvi, S.S.H. (Eds.),
Engineering Properties of Foods. Marcel Dekker, NY.
Taylor, J.R., 1997. An Introduction to Error Analysis, second ed. University Science
Books, Sausalito, California.
Wu, B., Yang, W., Jia, C., 2004. A three-dimensional numerical simulation of
transient heat and mass transfer inside a single rice kernel during the drying
process. Biosyst. Eng. 87 (2), 191–200.
W.P. da Silva et al. / Journal of Food Engineering 141 (2014) 65–73 73
```

