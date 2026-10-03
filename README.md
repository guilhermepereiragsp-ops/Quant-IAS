# Quantificação da Estenose do Segmento M1 em Imagens 3D TOF-MRA

Projeto/Estágio da Licenciatura em Engenharia Biomédica (LEBIOM), ISEP, ano letivo 2024/2025.

## Conceito

A estenose arterial intracraniana (IAS) no segmento M1 da artéria cerebral média é um fator de risco importante para o AVC, mas a sua avaliação em imagens TOF-MRA continua a depender da interpretação visual, que é subjetiva. Este projeto implementa um processo semiautomático para a quantificar:

1. **Pré-processamento:** reamostragem isotrópica da imagem (0.25 mm).
2. **Segmentação e esqueleto:** binarização por limiar (threshold de 180), esqueletização 3D da rede vascular e conversão do esqueleto numa malha de linhas (VTK PolyData).
3. **Medição do raio:** o utilizador escolhe dois pontos (*landmarks*) no esqueleto, e o caminho mais curto entre eles (Dijkstra) dá a *centerline* do segmento. O raio em cada ponto é a distância à isosuperfície do lúmen.
4. **Grau de estenose:** o utilizador define duas regiões de referência no gráfico do raio, de onde se obtém uma linha de tendência do raio normal. O grau de estenose é calculado em cada ponto, com base no raio e na área da secção transversal:

   ```
   Estenose (raio) = 100 · (1 − R / R_ref)
   Estenose (área) = 100 · (1 − (R / R_ref)²)
   ```

## Aplicação

Uma interface gráfica em PyQt5 reúne a análise: visualização 3D do esqueleto e da isosuperfície, seleção dos landmarks, gráfico do raio e do grau de estenose ao longo do vaso, e tabela de resultados (localização, extensão, raio mínimo e grau de estenose), exportável para CSV. A *spline* da centerline pode ser guardada em VTK.

Em 17 casos com IAS unilateral no segmento M1, os resultados foram concordantes com os dados clínicos em 9 dos 12 casos quantificáveis (2 subestimações e 1 sobreestimação). Nos 5 casos restantes, a ausência de reconstrução vascular foi associada a estenoses críticas (>90 %). Nos segmentos contralaterais, a ausência de estenose foi corretamente identificada em todas as imagens. É um protótipo de investigação e não substitui a avaliação clínica.

## Diretórios

```
.
├── datasets/
│   ├── STEN_worklist.txt              # Lista de casos (apenas Sten0001)
│   └── stens_vtk/
│       └── Sten0001.vtk               # Imagem TOF-MRA já convertida de DICOM para VTK
├── src/
│   ├── Preprocessing/
│   │   └── itkResampleImage.py        # 1. Reamostragem isotrópica (0.25 mm)
│   ├── Thinning/
│   │   ├── 1_itkThickness3D.py        # 2. Threshold + esqueletização 3D
│   │   ├── 2_vtkSkeleton2Polydata.py  # 3. Esqueleto (imagem) -> pontos (PolyData)
│   │   ├── 3_vtkIterateAllPoints.py   # 4. Pontos -> linhas (esqueleto final)
│   │   └── output/                    # Ficheiros gerados (esqueleto)
│   └── Interface/
│       ├── Interface_APP_v0.py        # Aplicação principal (executar este ficheiro)
│       ├── Interface_GUI_v0.py        # Layout da interface (PyQt5)
│       ├── Interface_SceneViewer.py   # Visualizador 3D (VTK)
│       ├── Stenosis_GraphPlotter.py   # Gráficos do raio e cálculo da estenose
│       └── funcs_ParametricSplines.py # Splines paramétricas
├── Poster_1220678.pdf
└── Quantificacao_da_Estenose_do_Segmento_M1_Guilherme_Pereira_1220678.pdf
```

Os caminhos usados por cada script são relativos à pasta onde é executado e estão definidos no início do ficheiro.

## Nota sobre os dados

- **Anonimização:** as imagens DICOM originais não estão incluídas. O projeto parte já da imagem em formato VTK (`stens_vtk`), pelo que o primeiro passo do pré-processamento (conversão DICOM para VTK) não é necessário.
- **Dimensão:** devido ao tamanho das imagens, só foi partilhado o primeiro paciente (**Sten0001**). Nestas condições, o projeto só funciona com este caso, e não com a totalidade do dataset usado no estudo.

## Como executar

Requisitos: Python 3 com `numpy`, `vtk`, `itk`, `itk-thickness3d` (versão igual à do `itk`, por exemplo `pip install itk-thickness3d==5.3`), `PyQt5` e `matplotlib`.

### 1. Gerar os ficheiros de entrada da aplicação

Executar os scripts por ordem, a partir da pasta de cada um. As pastas de saída (`datasets/stens_isotropic_025/` e `src/Thinning/output/`) têm de existir.

| Passo | Script | Entrada | Saída |
|---|---|---|---|
| 1 | `itkResampleImage.py` | `stens_vtk/Sten0001.vtk` | `stens_isotropic_025/Sten0001_isotropic_025.vtk` |
| 2 | `1_itkThickness3D.py` | imagem isotrópica | `Sten0001_025_180_none_skeleton.vtk` |
| 3 | `2_vtkSkeleton2Polydata.py` | esqueleto (imagem) | `Sten0001_025_180_none_polydata.vtk` |
| 4 | `3_vtkIterateAllPoints.py` | pontos do esqueleto | `Sten0001_025_180_none_polydata_line.vtk` |

Os passos 3 e 4 abrem uma janela de visualização no fim, que deve ser fechada para o script terminar. O passo 4 compara todos os pares de pontos do esqueleto, por isso pode demorar vários minutos.

### 2. Executar a aplicação

```bash
cd src/Interface
python Interface_APP_v0.py
```

1. Em **Input Data**, escolher o caso (`Case Idx` = 0, Sten0001) e clicar em **Load**.
2. Em **Isosurface**, ajustar o *isovalue* se necessário (por omissão, 180) e clicar em **Apply**.
3. Em **Landmarks**, escolher *Start* ou *End* e clicar num ponto do esqueleto na vista 3D. O caminho, a *centerline* e o gráfico do raio atualizam-se automaticamente.
4. Em **Spline**, ajustar o número de pontos e clicar em **Update**. **Reset Spline** repõe o caminho original.
5. No gráfico, arrastar as quatro linhas verticais para definir as duas regiões de referência. O grau de estenose e a sua localização aparecem na tabela, que pode ser exportada para CSV.

## Autor

Guilherme dos Santos Pereira  
Licenciatura em Engenharia Biomédica, Departamento de Física, ISEP, Porto, Portugal

Orientador: Prof. Doutor Carlos Vinhais (ISEP)

## Agradecimentos

Ao Prof. Doutor Carlos Vinhais, à Eng.ª Cristina Ribeiro, e ao Prof. Doutor António J. Bastos-Leite (Faculdade de Medicina da Universidade do Porto), que forneceu a base de dados de imagens.
