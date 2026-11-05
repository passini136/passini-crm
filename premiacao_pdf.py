"""PDFs da premiação por indicadores: relatório completo e pagamento (Financeiro).

Recebe o resultado de `team_award_results` de UM mês. Premiação é paga por
mês; o PDF de vários meses somados não corresponde a nenhum pagamento.

Os dois documentos saem do mesmo dado: o total do relatório completo e o do
pagamento são, por construção, o mesmo número.
"""
from __future__ import annotations

import io
import re
from typing import Any

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.units import mm
from reportlab.platypus import (KeepTogether, PageBreak, Paragraph, SimpleDocTemplate,
                                Spacer, Table, TableStyle)

AZ = colors.HexColor("#0f3044"); AZ2 = colors.HexColor("#1a5276"); CIN = colors.HexColor("#5b6b78")
LINHA = colors.HexColor("#d5dde3"); FUNDO = colors.HexColor("#eef4fa")
VERDE = colors.HexColor("#1e6b34"); VERDEF = colors.HexColor("#e6f4ea"); VERM = colors.HexColor("#a4262c")
APAGADO = colors.HexColor("#b7c2cb")
ORDEM = ["MATRIZ", "LAJEADO", "PELOTAS", "ZONA SUL", "ZONA NORTE", "XANGRILA"]
NOME_UN = {"XANGRILA": "XANGRI-LÁ"}
MESES = ["janeiro", "fevereiro", "março", "abril", "maio", "junho", "julho", "agosto",
         "setembro", "outubro", "novembro", "dezembro"]
# Ordem das colunas = ordem da cesta; o rótulo curto cabe na tabela em paisagem.
COLS = [("meta", "Meta"), ("margem", "Margem"), ("mix", "Itens"), ("positivacao", "Posit."),
        ("devolucoes", "Dev."), ("extraPositivacao", "Extra\nposit."), ("ead", "EAD"),
        ("ligacoes", "Lig."), ("redes", "Redes")]

S = dict(
    t=ParagraphStyle("t", fontName="Helvetica-Bold", fontSize=17, textColor=AZ, leading=21),
    st=ParagraphStyle("st", fontName="Helvetica", fontSize=9.5, textColor=CIN, leading=13),
    h=ParagraphStyle("h", fontName="Helvetica-Bold", fontSize=12, textColor=AZ, leading=15, spaceBefore=8, spaceAfter=4),
    p=ParagraphStyle("p", fontName="Helvetica", fontSize=8.5, textColor=CIN, leading=11),
    c=ParagraphStyle("c", fontName="Helvetica", fontSize=8, leading=10),
    k=ParagraphStyle("k", fontName="Helvetica-Bold", fontSize=16, textColor=AZ, leading=19),
    kl=ParagraphStyle("kl", fontName="Helvetica", fontSize=7.5, textColor=CIN, leading=9),
    u=ParagraphStyle("u", fontName="Helvetica", fontSize=10.5, textColor=AZ, leading=14),
    b=ParagraphStyle("b", fontName="Helvetica", fontSize=10, leading=14),
)


def _brl(v: float) -> str:
    return "R$ " + f"{float(v or 0):,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")


def _pct(p: float | None) -> str:
    return "sem meta" if p is None else f"{p:.1f}%".replace(".", ",")


def _un(u: str) -> str:
    return NOME_UN.get(u, u or "SEM UNIDADE")


def _nome(n: str) -> str:
    return re.sub(r"\s*\(.*\)$", "", n or "")


def _funcao(n: str) -> str:
    m = re.search(r"\((.*)\)$", n or "")
    f = m.group(1) if m else ""
    return {"VENDAS": "Vendas", "TELEVENDAS": "Televendas", "VENDAS DIG": "Vendas digital"}.get(f, f.title())


def _mes_extenso(comp: str) -> str:
    return f"{MESES[int(comp[5:7]) - 1]}/{comp[:4]}"


def _linhas(res: dict[str, Any]) -> list[dict[str, Any]]:
    """Achata a apuração do mês: uma linha por vendedor, já com o mês aberto."""
    out = []
    for v in res.get("sellers") or []:
        r = v.get("single") or (v.get("months") or [None])[0]
        if not r:
            continue
        pts = {i["code"]: int(i.get("points") or 0) for i in r.get("indicators") or []}
        if r.get("eligible"):
            sit = "Recebe · loja ≥95%" if r.get("eligibleByUnit") else "Recebe · individual ≥105%"
        else:
            m = r.get("eligibilityReason") or ""
            sit = ("Sem meta cadastrada no mês" if m.startswith("sem meta individual")
                   else "Loja <95% e individual <105%" if m.startswith("unidade em")
                   else "Não pontuou na meta de venda" if m.startswith("não pontuou")
                   else m[:60])
        out.append({
            "nome": v["sellerName"], "unidade": v.get("unitName") or "", "pts": int(r.get("points") or 0),
            "valor": float(r.get("value") or 0), "base": float(r.get("baseValue") or 0),
            "pctPago": float(r.get("payoutPct") or 0), "pct": r.get("goalPct"),
            "venda": float(r.get("revenue") or 0), "unidadePct": r.get("unitAttainment"),
            "porLoja": bool(r.get("eligibleByUnit")), "comp": pts, "situacao": sit,
        })
    return out


def _ordem_un(u: str) -> tuple[int, str]:
    return (ORDEM.index(u) if u in ORDEM else 99, u)


def _estilo(extra=None) -> TableStyle:
    return TableStyle([
        ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 7.6), ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("BACKGROUND", (0, 0), (-1, 0), AZ2), ("FONT", (0, 1), (-1, -1), "Helvetica", 8),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"), ("LINEBELOW", (0, 1), (-1, -1), 0.4, LINHA),
        ("TOPPADDING", (0, 0), (-1, -1), 3.5), ("BOTTOMPADDING", (0, 0), (-1, -1), 3.5),
        ("LEFTPADDING", (0, 0), (-1, -1), 4), ("RIGHTPADDING", (0, 0), (-1, -1), 4),
    ] + (extra or []))


def _rodape(titulo: str, comp: str, gerado: str):
    def f(cv, doc):
        cv.saveState(); cv.setFont("Helvetica", 7); cv.setFillColor(CIN)
        w, _ = doc.pagesize
        cv.drawString(doc.leftMargin, 10 * mm,
                      f"Passini · {titulo} · competência {_mes_extenso(comp)} · gerado pelo CRM em {gerado}")
        cv.drawRightString(w - doc.rightMargin, 10 * mm, f"página {doc.page}")
        cv.restoreState()
    return f


def relatorio_completo(res: dict[str, Any], gerado: str) -> bytes:
    comp = (res.get("competences") or [res.get("to")])[-1]
    V = _linhas(res)
    eleg = [v for v in V if v["valor"] > 0]
    total = sum(v["valor"] for v in eleg)
    unidades = sorted({v["unidade"] for v in V}, key=_ordem_un)
    pct_un = {}
    for v in V:
        pct_un.setdefault(v["unidade"], v["unidadePct"])

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=landscape(A4), leftMargin=12 * mm, rightMargin=12 * mm,
                            topMargin=12 * mm, bottomMargin=16 * mm,
                            title=f"Premiação de desempenho - {comp}")
    W = doc.width
    s: list[Any] = [
        Paragraph("Premiação por indicadores de desempenho · Vendas", S["t"]),
        Paragraph(f"Competência {_mes_extenso(comp)} · cesta {res.get('basket', '')} · "
                  "ordem: resumo → quem recebe → indicadores por unidade", S["st"]), Spacer(1, 8)]
    kp = [("Vendedores apurados", str(len(V))), ("Recebem", str(len(eleg))),
          ("Não recebem", str(len(V) - len(eleg))), ("Total a pagar", _brl(total))]
    kt = Table([[[Paragraph(l, S["kl"]), Paragraph(v, S["k"])] for l, v in kp]], colWidths=[W / 4] * 4)
    kt.setStyle(TableStyle([("BOX", (i, 0), (i, 0), 0.6, LINHA) for i in range(4)] + [
        ("BACKGROUND", (3, 0), (3, 0), VERDEF), ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6), ("LEFTPADDING", (0, 0), (-1, -1), 8)]))
    s += [kt, Spacer(1, 6)]

    # 1. Resumo por unidade
    s.append(Paragraph("1. Resumo por unidade", S["h"]))
    s.append(Paragraph("Gatilho: unidade com 95% ou mais da meta libera quem tem individual de 90% ou mais; "
                       "abaixo disso, só recebe quem fez 105% ou mais individual. Em todos os casos, é preciso "
                       "pontuar no indicador de meta de venda.", S["p"]))
    s.append(Spacer(1, 4))
    rows = [["Unidade", "% meta da unidade", "Gatilho da loja (≥95%)", "Vendedores", "Recebem",
             "Valor a pagar", "% do total"]]
    ex = [("ALIGN", (1, 0), (-1, -1), "CENTER"), ("ALIGN", (5, 1), (5, -1), "RIGHT"),
          ("FONT", (0, 1), (0, -1), "Helvetica-Bold", 8)]
    for i, u in enumerate(unidades, 1):
        g = [v for v in V if v["unidade"] == u]
        e = [v for v in g if v["valor"] > 0]
        val = sum(v["valor"] for v in e)
        p = pct_un.get(u)
        rows.append([_un(u), _pct(p), "sem meta" if p is None else ("Atingido" if p >= 95 else "Não atingido"),
                     str(len(g)), str(len(e)), _brl(val), f"{100 * val / total:.0f}%" if val and total else "—"])
        if p is not None:
            ex.append(("TEXTCOLOR", (2, i), (2, i), VERDE if p >= 95 else VERM))
    rows.append(["Total", "", "", str(len(V)), str(len(eleg)), _brl(total), "100%" if total else "—"])
    ex += [("FONT", (0, -1), (-1, -1), "Helvetica-Bold", 8.5), ("BACKGROUND", (0, -1), (-1, -1), FUNDO)]
    t = Table(rows, colWidths=[W * x for x in (.18, .14, .17, .11, .10, .17, .13)])
    t.setStyle(_estilo(ex))
    s.append(t)

    # 2. Quem recebe
    s.append(Paragraph("2. Quem recebe — ordenado por valor", S["h"]))
    s.append(Paragraph("Valor = base da faixa da meta individual × % pago (1 ponto = 1%, teto 150%). "
                       "Base: meta até R$ 159.999,99 = R$ 185; até R$ 309.999,99 = R$ 380; acima = R$ 530.", S["p"]))
    s.append(Spacer(1, 4))
    rows = [["#", "Vendedor", "Unidade", "% meta", "Venda líquida", "Como entrou", "Pontos",
             "Base", "% pago", "Valor a receber"]]
    for i, v in enumerate(sorted(eleg, key=lambda v: (-v["valor"], -v["pts"])), 1):
        como = (f"Loja ≥95% + individual {_pct(v['pct'])}" if v["porLoja"]
                else f"Individual {_pct(v['pct'])} (≥105%)")
        rows.append([str(i), Paragraph(f"<b>{_nome(v['nome'])}</b>", S["c"]), _un(v["unidade"]), _pct(v["pct"]),
                     _brl(v["venda"]), como, str(v["pts"]), _brl(v["base"]),
                     f"{v['pctPago']:.0f}%", _brl(v["valor"])])
    rows.append(["", "Total", "", "", "", "", str(sum(v["pts"] for v in eleg)), "", "", _brl(total)])
    t = Table(rows, colWidths=[W * x for x in (.035, .23, .09, .07, .11, .19, .06, .07, .06, .085)], repeatRows=1)
    t.setStyle(_estilo([("ALIGN", (3, 0), (4, -1), "RIGHT"), ("ALIGN", (6, 0), (-1, -1), "RIGHT"),
                        ("FONT", (-1, 1), (-1, -1), "Helvetica-Bold", 8.5), ("TEXTCOLOR", (-1, 1), (-1, -2), VERDE),
                        ("FONT", (0, -1), (-1, -1), "Helvetica-Bold", 8.5), ("BACKGROUND", (0, -1), (-1, -1), VERDEF)]))
    s += [t, PageBreak()]

    # 3. Indicadores por unidade
    s.append(Paragraph("3. Indicadores por unidade — pontos de cada vendedor", S["h"]))
    s.append(Paragraph("Dentro de cada unidade: primeiro quem recebe (maior valor), depois os demais por pontuação. "
                       "Zero aparece apagado. Extra positivação não tem teto.", S["p"]))
    s.append(Spacer(1, 4))
    maximos = {"meta": 50, "margem": 20, "mix": 15, "positivacao": 25, "devolucoes": 10,
               "ead": 10, "ligacoes": 10, "redes": 10}
    cab_cols = [f"{rot}\n({maximos[c]})" if c in maximos else rot for c, rot in COLS]
    larg = [.18, .06, .085] + [.04] * 9 + [.05, .07]
    larg.append(1 - sum(larg))
    for u in unidades:
        g = sorted([v for v in V if v["unidade"] == u], key=lambda v: (-v["valor"], -v["pts"]))
        rows = [["Vendedor", "% meta", "Venda líquida"] + cab_cols + ["Pontos", "Valor", "Situação"]]
        ex = [("ALIGN", (1, 0), (-4, -1), "CENTER"), ("ALIGN", (2, 1), (2, -1), "RIGHT"),
              ("ALIGN", (-3, 1), (-2, -1), "RIGHT"), ("FONT", (-3, 1), (-3, -1), "Helvetica-Bold", 8.5)]
        for i, v in enumerate(g, 1):
            rows.append([Paragraph(f"<b>{_nome(v['nome'])}</b><br/><font size=6.5 color='#5b6b78'>"
                                   f"{_funcao(v['nome'])}</font>", S["c"]),
                         _pct(v["pct"]), _brl(v["venda"])] + [str(v["comp"].get(c, 0)) for c, _ in COLS] +
                        [str(v["pts"]), _brl(v["valor"]) if v["valor"] else "—", Paragraph(v["situacao"], S["c"])])
            if v["valor"] > 0:
                ex += [("BACKGROUND", (0, i), (-1, i), VERDEF), ("FONT", (-2, i), (-2, i), "Helvetica-Bold", 8.5),
                       ("TEXTCOLOR", (-2, i), (-2, i), VERDE)]
            for j, (c, _) in enumerate(COLS, 3):
                if not v["comp"].get(c, 0):
                    ex.append(("TEXTCOLOR", (j, i), (j, i), APAGADO))
        p = pct_un.get(u)
        cab = Paragraph(
            f"<b>{_un(u)}</b> &nbsp;<font size=8 color='#5b6b78'>unidade em {_pct(p)} da meta"
            f"{'' if p is None else (' · gatilho atingido' if p >= 95 else ' · gatilho não atingido')}"
            f" · {len([x for x in g if x['valor'] > 0])} de {len(g)} recebem · "
            f"{_brl(sum(x['valor'] for x in g))}</font>", S["u"])
        t = Table(rows, colWidths=[W * x for x in larg], repeatRows=1)
        t.setStyle(_estilo(ex))
        s.append(KeepTogether([cab, Spacer(1, 3), t, Spacer(1, 10)]))

    rp = _rodape("Premiação de desempenho", comp, gerado)
    doc.build(s, onFirstPage=rp, onLaterPages=rp)
    return buf.getvalue()


def pagamento_financeiro(res: dict[str, Any], gerado: str) -> bytes:
    comp = (res.get("competences") or [res.get("to")])[-1]
    V = _linhas(res)
    eleg = [v for v in V if v["valor"] > 0]
    total = sum(v["valor"] for v in eleg)

    buf = io.BytesIO()
    doc = SimpleDocTemplate(buf, pagesize=A4, leftMargin=18 * mm, rightMargin=18 * mm,
                            topMargin=18 * mm, bottomMargin=18 * mm,
                            title=f"Premiação de vendas {comp} - pagamento")
    W = doc.width
    s: list[Any] = [Paragraph("Premiação de desempenho · Vendas", S["t"]),
                    Paragraph(f"Solicitação de pagamento · competência {_mes_extenso(comp)}", S["st"]), Spacer(1, 10)]
    if not eleg:
        s.append(Paragraph(f"Nenhum vendedor com premiação a receber na competência {_mes_extenso(comp)}.", S["b"]))
    else:
        s.append(Paragraph(f"Ao Financeiro: segue a relação dos <b>{len(eleg)} vendedores</b> com premiação apurada "
                           f"na competência {_mes_extenso(comp)}, no total de <b>{_brl(total)}</b>, para pagamento.",
                           S["b"]))
        s.append(Spacer(1, 10))
        rows = [["#", "Vendedor", "Unidade", "Valor"]]
        ex = []
        n = 0
        for u in sorted({v["unidade"] for v in eleg}, key=_ordem_un):
            g = sorted([v for v in eleg if v["unidade"] == u], key=lambda v: _nome(v["nome"]))
            for v in g:
                n += 1
                rows.append([str(n), _nome(v["nome"]), _un(u), _brl(v["valor"])])
            rows.append(["", f"Subtotal {_un(u)}", "", _brl(sum(v['valor'] for v in g))])
            k = len(rows) - 1
            ex += [("FONT", (0, k), (-1, k), "Helvetica-Bold", 9), ("BACKGROUND", (0, k), (-1, k), FUNDO)]
        rows.append(["", "TOTAL A PAGAR", "", _brl(total)])
        t = Table(rows, colWidths=[W * x for x in (.07, .53, .18, .22)])
        t.setStyle(_estilo([("FONT", (0, 1), (-1, -1), "Helvetica", 9.5), ("ALIGN", (3, 0), (3, -1), "RIGHT"),
                            ("ALIGN", (0, 0), (0, -1), "CENTER"), ("TOPPADDING", (0, 0), (-1, -1), 5),
                            ("BOTTOMPADDING", (0, 0), (-1, -1), 5), ("FONT", (0, 0), (-1, 0), "Helvetica-Bold", 9)]
                           + ex + [("FONT", (0, -1), (-1, -1), "Helvetica-Bold", 11),
                                   ("BACKGROUND", (0, -1), (-1, -1), VERDEF), ("TEXTCOLOR", (3, -1), (3, -1), VERDE),
                                   ("LINEABOVE", (0, -1), (-1, -1), 1, AZ)]))
        s += [t, Spacer(1, 14)]
        s.append(Paragraph(f"Valores brutos, apurados no CRM em {gerado}. Os demais vendedores apurados "
                           f"({len(V) - len(eleg)}) não têm valor a receber nesta competência.", S["p"]))
    s.append(Spacer(1, 40))
    ass = Table([["______________________________", "______________________________"],
                 ["Diretoria Comercial", "Financeiro · recebido em ____/____/______"]], colWidths=[W / 2, W / 2])
    ass.setStyle(TableStyle([("ALIGN", (0, 0), (-1, -1), "CENTER"), ("FONT", (0, 1), (-1, 1), "Helvetica", 8.5),
                             ("TEXTCOLOR", (0, 1), (-1, 1), CIN)]))
    s.append(ass)
    rp = _rodape("Pagamento de premiação", comp, gerado)
    doc.build(s, onFirstPage=rp, onLaterPages=rp)
    return buf.getvalue()
