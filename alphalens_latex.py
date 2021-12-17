# -*)- coding: utf-8 -*)-
#!/usr/bin/python
"""
https://jeltef.github.io/PyLaTeX/latest/index.html

    copyright: (c) 2014 by Jelte Fennema.
    license: MIT, see License for more details.

Demo from BBD Modeling Center: Chen Chen

"""
#%%
import os
import math
import pandas as pd

# begin-doc-include
from pylatex.utils import italic, NoEscape, bold
from pylatex import Document, Section, Subsection, Subsubsection, Command, Package, Figure, SubFigure, Alignat, \
     Itemize, Enumerate, Table, Tabular, Center, Head, Foot, PageStyle
from pylatex.section import Paragraph


__PATH_FILE = os.path.dirname(__file__)
_FOLDER_FIGURE = 'Output'
_SubFolder = 'patent_invention_utility_count_session'

#%%
def doc_config(doc, title, author):
    # Use ctex package to edit 中文
    doc.packages.add(Package('ctex'))
    # Centering subfigure's caption
    doc.packages.add(NoEscape(r'\usepackage[justification=centering]{caption}'))
    # header and foot
    doc.packages.add(NoEscape(r'\usepackage{fancyhdr}'))
    # line space
    doc.packages.add(NoEscape(r'\usepackage{setspace}'))
    # new date format
    doc.append(NoEscape(r'\renewcommand{\today}{\number\year/\number\month/\number\day}'))

    # 幼圆字体
    doc.append(NoEscape(r'\CJKfamily{zhyou}'))
    # 插入标题
    doc.append(NoEscape(r'\maketitle'))
    doc.preamble.append(Command('title', NoEscape(r'\Huge %s' % title)))
    doc.preamble.append(Command('author', author))
    doc.preamble.append(Command('date', NoEscape(r'\today')))
    # emphasis
    doc.append(NoEscape(r"\centerline{\color{red}{本报告仅作为模型中心内部技术交流使用}}"))

    # 插入图片
    with doc.create(Figure(position='h!')) as coverpage:
        coverpage.add_image(os.path.join(__PATH_FILE, 'LogoBBD_snapshot.png'), width='6in')
    doc.append(NoEscape(r'\thispagestyle{empty}'))  # 首页不显示页码
    doc.append(NoEscape(r'\clearpage'))

    # 页码罗马数字
    doc.append(NoEscape(r'\pagenumbering{roman}'))
    # 目录
    doc.append(NoEscape(r'\tableofcontents'))
    # 新页
    doc.append(NoEscape(r'\newpage'))
    # 图目录改名
    doc.append(NoEscape(r'\newcommand{\loflabel}{图}'))
    doc.append(NoEscape(r'\renewcommand{\numberline}[1]{\loflabel~#1：\hspace*{1em}}'))
    doc.append(NoEscape(r'\renewcommand\listfigurename{图目录}'))
    doc.append(NoEscape(r'\listoffigures'))
    # 新页
    doc.append(NoEscape(r'\newpage'))
    # 表目录改名
    doc.append(NoEscape(r'\newcommand{\lotlabel}{表}'))
    doc.append(NoEscape(r'\renewcommand{\numberline}[1]{\lotlabel~#1：\hspace*{1em}}'))
    doc.append(NoEscape(r'\renewcommand\listtablename{表目录}'))
    doc.append(NoEscape(r'\listoftables'))

    # 新页、不换列
    doc.append(NoEscape(r'\clearpage'))
    # 页码阿拉伯数字
    doc.append(NoEscape(r'\pagenumbering{arabic}'))
    # 页码起始页
    doc.append(NoEscape(r'\setcounter{page}{1}'))  # 从下面开始编页码
    # 行间距
    # doc.append(NoEscape(r'\setlength{\baselineskip}{20pt}'))    # 1 pt = 1/72 inch
    doc.append(NoEscape(r'\renewcommand{\baselinestretch}{1.5}'))

    # 表头
    header = generate_header()
    doc.preamble.append(header)
    doc.change_document_style("header")


def process_pep8_long_line(doc, text, length=160, indent=False):
    """
    :param doc: document object
    :param text: text
    :param length: PEP8 maximum length
    :param indent: new paragraph indentation
    :return: None
    """
    if indent:
        doc.append(NoEscape(r'\quad'))
    line_num = math.ceil(len(text)/length)
    for i in range(line_num):
        line = text[i*length: (i+1)*length]
        doc.append(NoEscape(line))


def number_equation_with_multilines(equation):
    """
    :param equation: equation
    :return: split equation if \\ sign in it
    """
    if r'\\' in equation:
        equation = r'\begin{split}' + equation + r'\end{split}'
    # print(equation)

    return equation


def generate_header():
    """
    Create doc header and footer
    :return: header object
    """
    # geometry_options = {"margin": "0.7in"}
    # doc = Document(geometry_options=geometry_options)
    # Add document header
    header = PageStyle("header")
    # Create left header
    with header.create(Head("L")):
        # header.append(r"Page date: \today")
        # header.append(LineBreak())
        # header.append(bold("BBD模型中心"))
        header.append(NoEscape(r'\includegraphics[scale=0.1]{BBD.png}'))
    # Create center header
    with header.create(Head("C")):
        header.append(NoEscape(r"\color{red}{本报告仅作为模型中心内部技术交流使用}"))
    # Create right header
    with header.create(Head("R")):
        header.append(bold("BBD模型中心"))
        # header.append(LineBreak())
    # # Create left footer
    # with header.create(Foot("L")):
    #     header.append("Left Footer")
    # Create center footer
    with header.create(Foot("C")):
        header.append(NoEscape(r'\thepage/\pageref{LastPage}'))
    # # Create right footer
    # with header.create(Foot("R")):
    #     header.append("Right Footer")

    return header


def fill_document(doc):
    """Add a section, a subsection, a subsubsection and some text to the document.

    :param doc: the document object
    :type doc: :class:`pylatex.document.Document` instance
    """
    text1 = r'近年来，随着国家重视程度的提升，中国已经成为了专利数量大国，虽然还不是专利技术强国，但可以反映出拥有自主专利的企业在中国能够获得更大的关注。专利数量是伴随研发投入之后产出的重要指标。本文利用专利数量，构建分类型的专利因子，验证专利因子与各期超额收益的相关性，后续将搭建回测平台验证专利因子在相关股票池内的预测能力和选股能力。'

    # text2 = r'如图\ref{fig:overall} 所示，2010年以来全市场A股公布的专利数量在逐年上升，从2010年的40000+例上升到了2019年的150000+例。同时，2010年底只有1700+家公司在年报中公布了公司全年的研发费用，这一数字在2018年底上升到了3000+家公司。专利数量的飞速增长，以及越来越多的上市公司在财务报告中公布研发费用，反映了中国上市企业正越来越注重自身的研发能力和创新能力，希望能够用这一能力获得更多的市场关注度。'

    text3 = r'专利类型主要有发明专利、实用新型专利、和外观设计专利。其中，发明专利分为发明授权和发明公布。发明授权是指通过国家知识产权局后授予具有法律效力的授权证书；发明公布是一种设计方案，知识提交给国家知识产权部门的技术方案，还没有授权批准。实用新型专利指对产品的形状、构造或者其结合所提出的适于实用的新的技术方案。实用新型与发明的不同之处在于，第一，实用新型只限于具有一定形状的产品，不能是一种方法，也不能是没有固定形状的产品；第二，实用新型的创造性要求不太高，而实用性较强。外观设计专利指工业品的外观设计，也就是工业品的式样。它与发明或实用新型完全不同，即外观设计不是技术方案。外观设计，是指对产品的形状、图案或者其结合以及色彩与形状、图案的结合所做出的富有美感并适于工业应用的新设计。'

    text4 = r'各行业2010年以来在各类型专利上的个数统计如图\ref{fig:industry} 所示，不同的行业发布的专利侧重种类也有所不同，家电、汽车和机械行业在实用新型专利上相比于其他行业有更多的专利个数，电子、家电和石油石化行业在发明专利上有更多的侧重，而家电、汽车和轻工制造行业在外观设计专利上明显多于其他行业。总体而且，家电、汽车、电子、石油石化、机械等行业有明显的专利优势，金融行业则很少发布自己的专利。本报告目前不针对专利种类和行业做区分，后续可以在不同行业和专利类型下研究专利因子的变化。'

    # Section 1
    with doc.create(Section('背景')):
        process_pep8_long_line(doc, text1)

        # insert a figure
        # figure_1 = os.path.join(__PATH_FILE, _FOLDER_FIGURE, 'Fig1.png')
        # with doc.create(Figure(position='h!')) as patent_over_market:
        #     patent_over_market.add_image(figure_1, width='8cm')
        #     patent_over_market.add_caption((NoEscape(
        #         r'\label{fig:overall} 全市场A股每年公布的专利数量及在年报中发布研发费用的公司数')))

        # process_pep8_long_line(doc, text2)

        # a new paragraph
        with doc.create(Paragraph('')):
            process_pep8_long_line(doc, text3, indent=True)

        # a new paragraph
        with doc.create(Paragraph('')):
            process_pep8_long_line(doc, text4, indent=True)

        # insert a figure
        figure_2 = os.path.join(__PATH_FILE, _FOLDER_FIGURE, _SubFolder, 'Fig2.png')
        with doc.create(Figure(position='h!')) as patent_over_market:
            patent_over_market.add_image(figure_2, width='13cm')
            patent_over_market.add_caption((NoEscape(
                r'\label{fig:industry} 中信一级行业2010年以来专利数量及专利覆盖度')))

    # Section 2
    with doc.create(Section('股票因子模型构建流程')):
        text5 = r'如图\ref{fig:factor_back_test} 本报告利用Alphalens进行股票因子的表现分析，目前仅对专利数量因子分专利类型进行单因子检验，多因子模型和投资组合管理待后续处理。'
        process_pep8_long_line(doc, text5)
        figure_3 = os.path.join(__PATH_FILE, _FOLDER_FIGURE, _SubFolder, 'Fig3.png')
        with doc.create(Figure(position='h!')) as patent_over_market:
            patent_over_market.add_image(figure_3, width='10cm')
            patent_over_market.add_caption((NoEscape(r'\label{fig:factor_back_test} 因子回测框架')))

    # Section 3
    with doc.create(Section('股票数据获取与样本筛选')):
        with doc.create(Subsection('股票数据获取')):
            with doc.create(Subsubsection('数据来源')):
                # item list starts with a bullet
                with doc.create(Itemize()) as itemize:
                    itemize.add_item("股票交易日线行情数据（Daily Bar）：Tushare。")
                    # itemize.add_item("上海银行间同业拆放利率（SHIBOR）数据：Tushare。")
            with doc.create(Subsubsection('数据类型')):
                with doc.create(Itemize()) as itemize:
                    itemize.add_item("前复权日收盘价。")
                    # itemize.add_item("ST、PT、停牌、复牌等事件发生日期。")

        with doc.create(Subsection('样本筛选')):
            # enum list
            with doc.create(Enumerate(enumeration_symbol=r"(\arabic*)", options={'start': 1})) as enum:
                enum.add_item("样本空间：全体A股（包括沪深主板、中小板、创业板、科创板）；")
                # enum.add_item("剔除选股日的ST/PT股票；")
                # enum.add_item("剔除上市不满一年的次新股；")
                enum.add_item("剔除选股日由于停牌等原因而无法买入的股票。")

        # text6 = r'按1个月（M）、3个月（Q）、6个月（SA）三种时间间隔类型选取横截面，各类型横截面时间节点如下：'
        # text7 = r'在第$t$期横截面上，股票的复权收益率$R_t=\frac{P_t}{P_{t-1}}$，其中$P_t$为$t$时刻的前复权日收盘价，$P_{t-1}$为相应时间间隔$t-1$时刻的前复权日收盘价，而超额收益率为$R_t$与SHIBOR利率之差。'
        # with doc.create(Subsection('复权收益率')):
            # process_pep8_long_line(doc, text6)
            # enmu list starts with an alphabet
            # with doc.create(Enumerate(enumeration_symbol=r"(\alph*)", options={'start': 1})) as enum:
                # enum.add_item("1个月（M）：取每月最后一个交易日作为当期横截面；")
                # enum.add_item("3个月（Q）：取每季度最后一个交易日作为当期横截面；")
                # enum.add_item("6个月（SA）：取每半年最后一个交易日作为当期横截面。")
                # enum.add_item("12个月（A）：取每年最后一个交易日作为当期横截面。")
            # process_pep8_long_line(doc, text7)

    # Section 4
    with doc.create(Section('裸指标计算')):
        text8 = r'按具体指标计算方案说明，计算裸指标值。之后在各横截面内对裸指标值进行异常值处理和标准化处理。'
        process_pep8_long_line(doc, text8)

    # Section 5
    with doc.create(Section('数据清洗')):
        with doc.create(Subsection('异常值处理')):
            # enum list
            with doc.create(Enumerate(enumeration_symbol=r"(\arabic*)", options={'start': 1})) as enum:
                # enum.add_item("如无特别说明，收益率不做异常值处理；")
                enum.add_item("标准差衡量；")
                # enum list start with a roman number
                with doc.create(Enumerate(enumeration_symbol=r"(\roman*)", options={'start': 1})) as enum_sub:
                    enum_sub.add_item("指标值偏离其上下百分之一分位点的值被视为异常值，异常值直接映射到相应分位点的值，其计算方法如下：")
                    with doc.create(Alignat(numbering=True, escape=False)) as agn:
                        # deal with multi-lines equation
                        agn.append(number_equation_with_multilines(
                            r'x[x > Quantile(X, 0.99)]\Rightarrow Quantile(X, 0.99)'
                            ))
                    with doc.create(Alignat(numbering=True, escape=False)) as agn:
                        agn.append(number_equation_with_multilines(
                            r'x[x < Quantile(X, 0.01)]\Rightarrow Quantile(X, 0.01)'
                            ))
                    # enum_sub.add_item("指标值偏离其均值3个绝对中位数(MAD)以上的值被视为异常值，异常值排序后按比例映射进3个绝对中位数至5个绝对中位数区间，其计算方法如下：")
                    # with doc.create(Alignat(numbering=True, escape=False)) as agn:
                    #     agn.append(number_equation_with_multilines(
                    #         r'MAD = Median(|x - Median(X)|)'))
                    # text9 = r'采取与上述$3\sigma$法等价的方法，将大于$Median(X)+3\cdot 1.4826 \cdot MAD$或小于$Median(X) -3 \cdot 1.4826 \cdot MAD$的值映射进3至5个$1.4826 \cdot MAD$区间：'
                    # process_pep8_long_line(doc, text9)
                    # with doc.create(Alignat(numbering=True, escape=False)) as agn:
                    #     agn.append(number_equation_with_multilines(
                    #         r'x[x > Mean(X) + & 3 \cdot 1.4826 \cdot MAD]\Rightarrow Mean(X) + 3 \cdot 1.4826 \cdot MAD + \\'
                    #         r'& 2 \cdot 1.4826 \cdot MAD \cdot \frac{x - Mean(X) - 3 \cdot 1.4826 \cdot MAD}{Max(X) - Mean(X) - 3 \cdot 1.4826 \cdot MAD}'))
                    # with doc.create(Alignat(numbering=True, escape=False)) as agn:
                    #     agn.append(number_equation_with_multilines(
                    #         r'x[x > Mean(X) - & 3 \cdot 1.4826 \cdot MAD]\Rightarrow Mean(X) - 3 \cdot 1.4826 \cdot MAD - \\'
                    #         r'& 2 \cdot 1.4826 \cdot MAD \cdot \frac{x - Mean(X) - 3 \cdot 1.4826 \cdot MAD}{Min(X) - Mean(X) - 3 \cdot 1.4826 \cdot MAD}'))
                    # enum_sub.add_item("如无特别说明，无穷大值作剔除处理（无穷大值通常来源于除数为0等情况）。")

        with doc.create(Subsection('缺失值处理')):
            # enum list starts with an arabic number
            with doc.create(Enumerate(enumeration_symbol=r"(\arabic*)", options={'start': 1})) as enum:
                enum.add_item("收益率缺失值作剔除处理（例如停牌造成的收益率缺失）；")
                enum.add_item("指标缺失值作剔除处理（例如未收集到数据的上市企业）；")
                enum.add_item("剔除收益率缺失或指标缺失的数据条。")

    # Section 6
    with doc.create(Section('因子标准化')):
        text10 = r'对异常值处理和缺失值处理后的指标采用Min-Max标准化方法，得到因子取值，其转换公式如下：'
        process_pep8_long_line(doc, text10)
        with doc.create(Alignat(numbering=True, escape=False)) as agn:
            agn.append(number_equation_with_multilines(r'x:transform\Rightarrow \frac{x:transform - Min(X:transform)}{Max(X:transform) - Min(X:transform)}'))

    # Section 7
    with doc.create(Section('单因子有效性检验')):
        with doc.create(Subsection('换仓周期')):
            text12 = r'按1个月、3个月、6个月三种时间间隔类型作为换仓周期，各类型横截面时间节点如下：'
            process_pep8_long_line(doc, text12)
            with doc.create(Enumerate(enumeration_symbol=r"(\alph*)", options={'start': 1})) as enum:
                enum.add_item("1个月：取每月最后一个交易日作为当期横截面；")
                enum.add_item("3个月：取每三个月最后一个交易日作为当期横截面；")
                enum.add_item("6个月：取每六个月最后一个交易日作为当期横截面。")
            
        with doc.create(Subsection('分层检验')):
            text11 = r'由于指标值的高度集中性，仅用横截面数据进行固定分位点的划分会出现分位点指标值重叠的问题。为了处理这种情况，指标数据驱动的生成分箱划分点，采用根据全量指标值的相应分位点作为划分点的方式进行分层。本次检验采用全量指标值的$50\%$, $70\%$, $90\%$, $95\%$分位点分为五层，对分调仓周期收益率、收益率差值、累计收益率进行分层分析'
            process_pep8_long_line(doc, text11)

            # a new paragraph
            # with doc.create(Paragraph('')):
            #     text12 = r'其中，$\tilde{r_t}$代表第t期横截面上各股票相比于无风险收益的超额收益，即$\tilde{r_t}=\tilde{R_t}-R_0$，$\tilde{R_t}$采用股票从t-1时刻至t时刻的复权收益率，$R_0$采用t-1时刻至t时刻的上海银行间同业拆放利率（SHIBOR）；$x_{t-1}$代表基于t-1时刻可获取数据所计算的因子值（又称风险暴露系数）；$\tilde{f_t}$由回归方程估计所得，也被解读为因子收益；$u_t$为残差收益。'
            #     process_pep8_long_line(doc, text12, indent=True)
            # with doc.create(Paragraph('')):
            #     text13 = r'横截面回归时间间隔包括以下4种类型：1个月、3个月、6个月、12个月。收益率及因子数据采用相应的期末最新可获取值。'
            #     process_pep8_long_line(doc, text13, indent=True)
        # with doc.create(Subsection('横截面回归')):
        #     text11 = r'在第t期横截面上，对全体非空样本做单因子回归，公式如下：'
        #     process_pep8_long_line(doc, text11)
        #     with doc.create(Alignat(numbering=True, escape=False)) as agn:
        #         agn.append(number_equation_with_multilines(r'\tilde{r_t}=x_{t-1} \cdot \tilde{f_t}+u_t'))
        #     # a new paragraph
        #     with doc.create(Paragraph('')):
        #         text12 = r'其中，$\tilde{r_t}$代表第t期横截面上各股票相比于无风险收益的超额收益，即$\tilde{r_t}=\tilde{R_t}-R_0$，$\tilde{R_t}$采用股票从t-1时刻至t时刻的复权收益率，$R_0$采用t-1时刻至t时刻的上海银行间同业拆放利率（SHIBOR）；$x_{t-1}$代表基于t-1时刻可获取数据所计算的因子值（又称风险暴露系数）；$\tilde{f_t}$由回归方程估计所得，也被解读为因子收益；$u_t$为残差收益。'
        #         process_pep8_long_line(doc, text12, indent=True)
        #     with doc.create(Paragraph('')):
        #         text13 = r'横截面回归时间间隔包括以下4种类型：1个月、3个月、6个月、12个月。收益率及因子数据采用相应的期末最新可获取值。'
        #         process_pep8_long_line(doc, text13, indent=True)

    # with doc.create(Subsection('回归模型选择')):
    #     # enum list starts with an arabic number
    #     with doc.create(Enumerate(enumeration_symbol=r'(\arabic*)', options={'start': 1})) as enum:
    #         enum.add_item("最小二乘线性回归（OLS）：Ordinary Least Square")
    #         text14 = r'OLS 是最常用、最简单的方法，该方法的缺点是 OLS 需假设回归方程的残差均具有相同的方差，但股票收益率常常存在异常值，且不同股票的收益率波动性也不尽相同。使用 OLS 时，异常值会对回归结果和回归测试的显著性检验带来较明显影响。'
    #         process_pep8_long_line(doc, '\n\n')
    #         process_pep8_long_line(doc, text14)
    #         enum.add_item("加权最小二乘线性回归（WLS）：Weighted Least Square")
    #         text15 = r'假设股票残差收益的方差与股票市值的平方根成反比，因此通过 WLS 将市值平方根作为残差项的回归权重。'
    #         process_pep8_long_line(doc, '\n\n')
    #         process_pep8_long_line(doc, text15)
    #         enum.add_item("稳健线性回归（RLM）：Robust Linear Model")
    #         text16 = r'RLM 通过迭代的赋权回归可以有效的减小异常值对参数估计结果有效性和稳定性的影响。'
    #         process_pep8_long_line(doc, '\n\n')
    #         process_pep8_long_line(doc, text16)

    with doc.create(Subsection('有效性检验')):
        text16 = r'根据不同换仓周期，可得到每一换仓周期的收益率情况、IC值序列。针对这两类值绘制以下图表判断该因子的有效性：'
        process_pep8_long_line(doc, text16)
        # item list starts with a bullet
        with doc.create(Itemize()) as itemize:
            itemize.add_item(NoEscape(r'各换仓周期的分层收益率分布情况；'))
            itemize.add_item(NoEscape(r'各换仓周期的分层平均收益率情况；'))
            itemize.add_item(NoEscape(r'6个月换仓周期的层间收益率差值情况；'))
            itemize.add_item(NoEscape(r'1个月换仓周期的分层累计收益率情况；'))
            itemize.add_item(NoEscape(r'各换仓周期的IC值分布情况。'))
        # with doc.create(Paragraph('')):
        #     text17 = r'IC值（信息系数）是指第$t$期横截面上因子值$x_{t-1}$与股票收益$\tilde{r_t}$的相关系数。IC值计算有两种常见方法：相关系数（Pearson Correlation）和秩相关系数（Spearman Rank Correlation）。本文采用Spearman相关系数。'
        #     process_pep8_long_line(doc, text17, indent=True)
        # with doc.create(Paragraph('')):
        #     text18 = r'类似地，各期IC值构成序列，针对IC序列采用以下指标判断因子有效性：'
        #     process_pep8_long_line(doc, text18, indent=True)
        # # item list starts with a bullet
        # with doc.create(Itemize()) as itemize:
        #     itemize.add_item(NoEscape(r'IC序列的均值；'))
        #     itemize.add_item(NoEscape(r'IC序列的标准差；'))
        #     itemize.add_item(NoEscape(r'IC绝对值大于0.02的比例；'))
        #     itemize.add_item(NoEscape(r'IC序列的$t$检验值。'))

    # Section 8
    with doc.create(Section('结果展示')):
        figure_4 = os.path.join(__PATH_FILE, _FOLDER_FIGURE, _SubFolder, 'PeriodWiseReturnByFactorQuantile.png')
        with doc.create(Figure(position='h!')) as patent_over_market:
            patent_over_market.add_image(figure_4, width='8cm')
            patent_over_market.add_caption((NoEscape(
                r'\label{fig4} 各换仓周期的分层收益率分布')))

        figure_5 = os.path.join(__PATH_FILE, _FOLDER_FIGURE, _SubFolder, 'MeanPeriodWiseReturnByFactorQuantile.png')
        with doc.create(Figure(position='h!')) as patent_over_market:
            patent_over_market.add_image(figure_5, width='8cm')
            patent_over_market.add_caption((NoEscape(
                r'\label{fig5} 各换仓周期的平均分层收益率')))

        figure_6 = os.path.join(__PATH_FILE, _FOLDER_FIGURE, _SubFolder, 'ReturnSpread.png')
        with doc.create(Figure(position='h!')) as patent_over_market:
            patent_over_market.add_image(figure_6, width='8cm')
            patent_over_market.add_caption((NoEscape(
                r'\label{fig6} 6个月换仓周期的层间收益率差值')))

        figure_7 = os.path.join(__PATH_FILE, _FOLDER_FIGURE, _SubFolder, 'CumulativeReturnByQuantile_1M.png')
        with doc.create(Figure(position='h!')) as patent_over_market:
            patent_over_market.add_image(figure_7, width='8cm')
            patent_over_market.add_caption((NoEscape(
                r'\label{fig7} 1个月换仓周期的分层累计收益率')))

        figure_8 = os.path.join(__PATH_FILE, _FOLDER_FIGURE, _SubFolder, 'Ic.png')
        with doc.create(Figure(position='h!')) as patent_over_market:
            patent_over_market.add_image(figure_8, width='8cm')
            patent_over_market.add_caption((NoEscape(
                r'\label{fig8} 各换仓周期的IC值分布')))

        figure_9 = os.path.join(__PATH_FILE, _FOLDER_FIGURE, _SubFolder, 'IcQq.png')
        with doc.create(Figure(position='h!')) as patent_over_market:
            patent_over_market.add_image(figure_9, width='8cm')
            patent_over_market.add_caption((NoEscape(
                r'\label{fig9} 各换仓周期的IC值QQ图')))

        figure_10 = os.path.join(__PATH_FILE, _FOLDER_FIGURE, _SubFolder, 'MonthlyMeanIcHeatmap.png')
        with doc.create(Figure(position='h!')) as patent_over_market:
            patent_over_market.add_image(figure_10, width='8cm')
            patent_over_market.add_caption((NoEscape(
                r'\label{fig10} 各换仓周期的IC值月度热力图')))
        # process_pep8_long_line(doc, r'以专利数量为例首先确定最优方法与最优参数组合。')
        # text19 = r'经过多组回测组合，OLS、WLS、RLM三种模型方法中以RLM结果最为理想，从下表数据中可以明显看出三种模型方法在不同周期长度(PAT\_M（月）/Q（季）/SA（半年）/A（年）)专利因子对于长周期超额收益（er\_12m）回归中RLM方法始终最优结果：t值最高，t值大于2的比例最高，因子收益表现RLM只是略逊于OLS（表\ref{Table1}）。综合考虑我们决定利用RLM方法通过不同参数的对比寻找优化因子的路径。'
        # with doc.create(Enumerate(enumeration_symbol=r'(\arabic*)', options={'start': 1})) as enum:
            # enum.add_item(text19)
        # with doc.create(Subsection('归回方法对比')):
        #     process_pep8_long_line(doc, text19)
        # # create a table
        # with doc.create(Table(position="htb")) as tbl_1:
        #     tbl_1.add_caption((NoEscape(r'\label{Table1} RLM、OLS、WLS回归方法对比')))
        #     with doc.create(Center()):
        #         tbl_data_1 = pd.read_csv('table1.csv')
        #         # columns = tbl_data_1.columns
        #         columns = ['er_over_factor', 't_value_mean', 't_gt2', 'factor_loading_mean']
        #         n_columns = len(columns)
        #         table1 = Tabular('|' + 'c|' * n_columns, booktabs=False)
        #         table1.add_hline()
        #         # http://www.latexcolor.com/
        #         table1.add_row(columns, color='gray')
        #         table1.add_hline()
        #         # fill the table with colors
        #         for index, row in tbl_data_1[columns].iterrows():
        #             if 'PAT_M' in row.er_over_factor:
        #                 table1.add_row([round(item, 3) if type(item) == float else item for item in row], color='cyan')
        #             elif 'PAT_Q' in row.er_over_factor:
        #                 table1.add_row([round(item, 3) if type(item) == float else item for item in row], color='green')
        #             elif 'PAT_SA' in row.er_over_factor:
        #                 table1.add_row([round(item, 3) if type(item) == float else item for item in row], color='yellow')
        #             elif 'PAT_A' in row.er_over_factor:
        #                 table1.add_row([round(item, 3) if type(item) == float else item for item in row], color='red')
        #         table1.add_hline()
        #         doc.append(table1)

        # text20 = r'利用上述结论，以RLM回归通过对比异常值处理的两种不同方法STD（方差）和MAD（绝对中位数）在不同周期长度(PAT\_M（月）/Q（季）/SA（半年）/A（年）)专利因子对于长周期超额收益（er\_12m）的贡献确定STD方法的效果明显优于MAD（表\ref{Table2}）。'
        # with doc.create(Subsection('异常值处理对比')):
        #     process_pep8_long_line(doc, text20)
        # # create a table
        # with doc.create(Table(position="htb")) as tbl_2:
        #     tbl_2.add_caption(NoEscape(r'\label{Table2} STD和MAD异常值处理方法RLM回归结果对比'))
        #     with doc.create(Center()):
        #         tbl_data_2 = pd.read_csv('table2.csv')
        #         columns = ['er_over_factor', 't_value_mean', 't_gt2', 'factor_loading_mean']
        #         n_columns = len(columns)
        #         table2 = Tabular('|' + 'c|' * n_columns, booktabs=False)
        #         table2.add_hline()
        #         # http://www.latexcolor.com/
        #         table2.add_row(columns, color='gray')
        #         table2.add_hline()
        #         # fill the table with colors
        #         for index, row in tbl_data_2[columns].iterrows():
        #             if 'PAT_M' in row.er_over_factor:
        #                 table2.add_row([round(item, 3) if type(item) == float else item for item in row], color='cyan')
        #             elif 'PAT_Q' in row.er_over_factor:
        #                 table2.add_row([round(item, 3) if type(item) == float else item for item in row], color='green')
        #             elif 'PAT_SA' in row.er_over_factor:
        #                 table2.add_row([round(item, 3) if type(item) == float else item for item in row], color='yellow')
        #             elif 'PAT_A' in row.er_over_factor:
        #                 table2.add_row([round(item, 3) if type(item) == float else item for item in row], color='red')
        #         table2.add_hline()
        #         doc.append(table2)

        # text21 = r'在大量回测对比中发现，长周期无论在因子统计周期还是超额收益周期中都具有良好的表现，这也符合人们对于优质公司的预期。因为专利数量代表了以一个公司在研发中投入的成果，越多的专利数量在长期来看有利于公司形成自己在行业竞争中的优势壁垒，同时这种优势壁垒会在未来一段时间内使得公司在垂直发展中的价值得以体现，而不是短时间消息刺激或者政策推动。从下图中看无论固定专利因子统计周期还是超额收益周期，长周期均拥有最佳表现（表\ref{Table3}）。'
        # with doc.create(Subsection('统计周期对比')):
        #     process_pep8_long_line(doc, text21)
        # # create a table
        # with doc.create(Table(position="htb")) as tbl_3:
        #     tbl_3.add_caption(NoEscape(r'\label{Table3} 因子统计周期、超额收益周期RLM回归对比'))
        #     with doc.create(Center()):
        #         tbl_data_3 = pd.read_csv('table3.csv')
        #         columns = ['er_over_factor', 't_value_mean', 't_gt2', 'factor_loading_mean']
        #         n_columns = len(columns)
        #         table3 = Tabular('|' + 'c|' * n_columns, booktabs=False)
        #         table3.add_hline()
        #         # http://www.latexcolor.com/
        #         table3.add_row(columns, color='gray')
        #         table3.add_hline()
        #         # fill the table with colors
        #         for index, row in tbl_data_3[columns].iterrows():
        #             if 'PAT_M' in row.er_over_factor:
        #                 table3.add_row([round(item, 3) if type(item) == float else item for item in row], color='cyan')
        #             elif 'PAT_Q' in row.er_over_factor:
        #                 table3.add_row([round(item, 3) if type(item) == float else item for item in row], color='green')
        #             elif 'PAT_SA' in row.er_over_factor:
        #                 table3.add_row([round(item, 3) if type(item) == float else item for item in row], color='yellow')
        #             elif 'PAT_A' in row.er_over_factor:
        #                 table3.add_row([round(item, 3) if type(item) == float else item for item in row], color='red')
        #         table3.add_hline()
        #         doc.append(table3)

        # text22 = r'下面主要讨论专利数量因子和研发效能因子分别在不同因子统计周期和超额收益周期上的表现。由于维度比较多，首先固定超额收益周期观察不同因子统计周期的回归表现（见图\ref{Fig4}；上排专利数量，下排研发效能（研发投入除以专利数量））。通过对比很容易发现专利数量因子明显比研发效能表现好的多，同时由于研发效能因子基于上市公司的财务数据具有一定的滞后性（季度发布），这给建模和解释带来更多不确定性。其次，固定因子统计周期观察不同超额收益周期的表现（见图\ref{Fig5}；上排专利数量，下排研发效能（研发投入除以专利数量））。专利因子与越长周期的超额收益相关性越高，短周期的相关性接近随机游走的状态，并且在所有柱状图发现误差均大于均值，说明稳定性依然是因子挖掘中的重要问题。由此带来的因子的时效性问题需要在一段较长的时间上才能得到验证。尽管如此，由于T值>2可以认为因子和超额收益存在显著性；并且IC值>0.05以上时可以认为因子选股能力较强，我们依然可以有信心地认为专利因子可以作为一个有效的选股因子在二级市场中发挥价值。这符合市场认为专利是反应公司价值的一个指标，因此专利因子不适宜作为短期选股指标。'
        # # figure_4a = os.path.join(__PATH_FILE, _FOLDER_FIGURE, 'factor_loading_RLM_std_er_12m.png')
        # figure_4b = os.path.join(__PATH_FILE, _FOLDER_FIGURE, 'tvalue_RLM_std_er_12m.png')
        # figure_4c = os.path.join(__PATH_FILE, _FOLDER_FIGURE, 'ic_RLM_std_er_12m.png')
        # with doc.create(Subsection('讨论')):
        #     process_pep8_long_line(doc, text22)
        #     with doc.create(Figure(position='htb')) as Fig4:
        #         with doc.create(Center()):
        #             # create a sub-figure, could be next to each other or could be one on the top, one below
        #             with doc.create(SubFigure(position="htb", width=NoEscape(r'\linewidth'))) as subfigure:
        #                 # with doc.create(MiniPage(width=r"0.5\textwidth")):
        #                     # subfigure.add_image(figure_4a)#, width=NoEscape(r'0.7\linewidth'))
        #                     # subfigure.add_caption('因子暴露系数\n')
        #                     subfigure.add_image(figure_4b)#, width=NoEscape(r'0.7\linewidth'))
        #                     subfigure.add_caption('T值序列')
        #                     subfigure.add_image(figure_4c)#, width=NoEscape(r'0.7\linewidth'))
        #                     subfigure.add_caption('IC值序列')
        #         Fig4.add_caption(NoEscape(r"\label{Fig4} 固定年度超额收益（ER\_12M）对比因子统计周期（M/Q/SA/A）"))

        # # figure_5a = os.path.join(__PATH_FILE, _FOLDER_FIGURE, 'factor_loading_RLM_std_er_12m.png')
        # figure_5b = os.path.join(__PATH_FILE, _FOLDER_FIGURE, 'tvalue_RLM_std_A.png')
        # figure_5c = os.path.join(__PATH_FILE, _FOLDER_FIGURE, 'ic_RLM_std_A.png')
        # with doc.create(Figure(position='htb')) as Fig5:
        #     with doc.create(Center()):
        #         # create a sub-figure, could be next to each other or could be one on the top, one below
        #         with doc.create(SubFigure(position="htb", width=NoEscape(r'\linewidth'))) as subfigure:
        #             # with doc.create(MiniPage(width=r"0.5\textwidth")):
        #             # subfigure.add_image(figure_5a)#, width=NoEscape(r'0.7\linewidth'))
        #             # subfigure.add_caption('因子暴露系数\n')
        #             subfigure.add_image(figure_5b)  # , width=NoEscape(r'0.7\linewidth'))
        #             subfigure.add_caption('T值序列')
        #             subfigure.add_image(figure_5c)  # , width=NoEscape(r'0.7\linewidth'))
        #             subfigure.add_caption('IC值序列')
        #     Fig5.add_caption(
        #         NoEscape(r"\label{Fig5} 固定因子统计周期（A）对比超额收益统计周期（1m[M]/3m[Q]/6m[SA]/12m[A]）"))


if __name__ == '__main__':
    # clean files
    files = os.listdir(__PATH_FILE)
    for file in files:
        if file.split('.')[-1] in ['pdf', 'tex', 'xdv']:
            # print(file)
            os.remove(file)

    title = '专利单因子检验报告'
    author = '邓雅心/模型中心'
    # 创立文档[页边距]
    geometry_options = {"tmargin": "1.5in",
                        "lmargin": "1.25in",
                        "rmargin": "1in"}
    doc = Document(geometry_options=geometry_options)
    # 文档样式
    doc_config(doc, title, author)
    # 文档内容
    fill_document(doc)
    # 生成PDF
    # doc.generate_pdf(title, clean_tex=False, compiler='xelatex') # 目录生成有问题
    doc.generate_pdf(title, clean_tex=False, compiler='pdflatex', compiler_args=['-xelatex'])

