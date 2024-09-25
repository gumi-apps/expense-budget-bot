import matplotlib.pyplot as plt
from io import BytesIO


colors = [
    "slategrey",
    "lightsteelblue",
    "cornflowerblue",
    "royalblue",
    "lavender",
    "navy",
    "blue",
    "slateblue",
    "darkslateblue",
    "mediumblue",
    "blueviolate",
    "indigo",
    "darkorchid",
    "plum",
    "violate",
    "fuchisa",
    "orchid",
    "pink",
    "lightpink",
    "crimson",
    "hotpink",
]


def get_pie(sizes, labels):
    plt.pie(
        sizes,
        labels=labels,
        colors=colors,
        autopct="%1.1f%%",
        startangle=140,
    )
    plt.axis("equal")
    img_buffer = BytesIO()
    plt.savefig(img_buffer, format="png")
    img_buffer.seek(0)

    img_data = img_buffer.getvalue()

    img_buffer.close()

    return img_data
