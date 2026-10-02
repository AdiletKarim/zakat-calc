import streamlit as st

# Методика: учебные значения по умолчанию, окончательно их утверждает специалист
NISAB_GOLD_G = 85
NISAB_SILVER_G = 595
RATES = {"Лунный год, 2,5%": 0.025, "Солнечный год, 2,577%": 0.02577}


def calculate_zakat(cash, gold_g, silver_g, gold_price, silver_price,
                    receivables, goods, investments, debts, nisab_basis, rate):
    """Считает закят и возвращает расшифровку расчёта."""
    gold_value = gold_g * gold_price
    silver_value = silver_g * silver_price
    assets = cash + gold_value + silver_value + receivables + goods + investments
    net = max(assets - debts, 0)

    if nisab_basis == "gold":
        nisab = NISAB_GOLD_G * gold_price
    else:
        nisab = NISAB_SILVER_G * silver_price

    reached = net >= nisab
    zakat = net * rate if reached else 0
    return {"assets": assets, "debts": debts, "net": net,
            "nisab": nisab, "reached": reached, "zakat": zakat}


def fmt(x):
    return f"{x:,.0f} ₸".replace(",", " ")


def money(label):
    return st.number_input(label, min_value=0.0, step=10000.0, format="%.0f")


st.title("Калькулятор закята")
st.caption("Версия v0.1, обновлено через git push.")

st.subheader("Методика")
basis_label = st.radio("Нисаб считается по", ["золоту (85 г)", "серебру (595 г)"], horizontal=True)
nisab_basis = "gold" if basis_label.startswith("золот") else "silver"
rate_label = st.radio("Ставка", list(RATES), horizontal=True)

st.subheader("Цена грамма, ₸")
c1, c2 = st.columns(2)
gold_price = c1.number_input("Золото", min_value=0.0, step=100.0, format="%.0f")
silver_price = c2.number_input("Серебро", min_value=0.0, step=10.0, format="%.0f")

st.subheader("Активы")
cash = money("Наличные и деньги на счетах, ₸")
g1, g2 = st.columns(2)
gold_g = g1.number_input("Золото, граммы", min_value=0.0, step=1.0)
silver_g = g2.number_input("Серебро, граммы", min_value=0.0, step=1.0)
receivables = money("Деньги, которые вам должны вернуть, ₸")
goods = money("Товары для продажи, ₸")
investments = money("Инвестиции по рыночной стоимости (упрощённо), ₸")

st.subheader("Обязательства")
debts = money("Долги к оплате, ₸")

basis_price = gold_price if nisab_basis == "gold" else silver_price
if basis_price == 0:
    st.warning("Введите цену грамма металла, по которому считается нисаб, и расчёт появится.")
    st.stop()

r = calculate_zakat(cash, gold_g, silver_g, gold_price, silver_price,
                    receivables, goods, investments, debts,
                    nisab_basis, RATES[rate_label])

st.subheader("Результат")
if r["reached"]:
    st.success(f"Закят к выплате: {fmt(r['zakat'])}")
else:
    st.info("Чистые активы ниже нисаба, закят не обязателен.")

st.table({
    "Показатель": ["Активы всего", "Долги к оплате", "Чистые активы", "Нисаб"],
    "Сумма": [fmt(r["assets"]), fmt(r["debts"]), fmt(r["net"]), fmt(r["nisab"])],
})
