import matplotlib.pyplot as plt

plt.rcParams["font.family"] = "AppleGothic"   # 맥이면 이거, 윈도우면 "Malgun Gothic"
plt.rcParams["axes.unicode_minus"] = False

tall = [150, 160, 170, 180, 181]   # 아무 숫자 리스트로 바꿔도 됨

fig, ax = plt.subplots(figsize=(7, 4))
ax.plot(tall)

for i, p in enumerate(tall):
    ax.annotate(f"{p:,}", (i, p),
                textcoords="offset points",
                xytext=(0, 8), ha="center")

ax.set_title("키 변화")
fig.savefig("my_first_chart.png")