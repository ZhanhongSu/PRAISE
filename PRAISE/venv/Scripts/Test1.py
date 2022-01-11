import pandas as pd
from sklearn import tree
import graphviz

data = pd.read_csv("Database - Blad1.csv")
#dataTest = pd.read_csv("Scripts/Database - Blad2.csv")

feature = data[["articulationRate", "F0", "fillerWords", "speechMode"]]
target = data["engagementLevel"]

model = tree.DecisionTreeClassifier()
model = model.fit(feature, target)

#dot_data = tree.export_graphviz(model, out_file= None)
#graph = graphviz.Source(dot_data)
#graph.render("Frank_Decision_Tree_1")

#featureTest = dataTest[["articulationRate", "F0", "fillerWords", "speechMode"]]
featureTest = [[4.6,928,1.7937898051455632,3]]
y = model.predict(featureTest)
print(y)
