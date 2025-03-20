from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
import pandas as pd
import matplotlib.pyplot as plt

# Dados simulados (substitua pelo seu DataFrame real)
df = pd.DataFrame({
    "Setor": ["Rebobinadeira", "Impressão", "Laminação"],
    "OS_Abertas": [120, 80, 95],
    "Tempo_Médio_Manutenção (h)": [4.5, 3.8, 5.2]
})

# Gerar gráfico
plt.figure(figsize=(6, 4))
plt.bar(df["Setor"], df["Tempo_Médio_Manutenção (h)"], color=['blue', 'red', 'green'])
plt.xlabel("Setor")
plt.ylabel("Tempo Médio (h)")
plt.title("Tempo Médio de Manutenção por Setor")
plt.savefig("grafico.png")  # Salva gráfico para incluir no PDF
plt.close()

# Criar PDF
pdf_file = "Relatorio_Manutencao.pdf"
c = canvas.Canvas(pdf_file, pagesize=letter)
c.drawString(100, 750, "Relatório de Manutenção - Análise de OS")

# Adicionar imagem do gráfico
c.drawImage("grafico.png", 100, 500, width=400, height=200)

# Adicionar tabela de dados ao relatório
y_position = 480
for index, row in df.iterrows():
    c.drawString(100, y_position, f"{row['Setor']}: {row['OS_Abertas']} OS | Tempo Médio: {row['Tempo_Médio_Manutenção (h)']}h")
    y_position -= 20

c.save()
print(f"Relatório salvo como {pdf_file}")
