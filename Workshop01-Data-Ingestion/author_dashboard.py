import marimo as mo

app = mo.App()


@app.cell
def __():
    import marimo as mo
    import ibis
    import dlt
    import plotly.express as px
    return mo, ibis, dlt, px


@app.cell
def __(dlt):
    # Use dlt's dataset handle so schema/database are resolved from pipeline state.
    pipeline = dlt.pipeline(
        pipeline_name="open_library_pipeline",
        destination="duckdb",
    )
    dataset = pipeline.dataset()
    conn = dataset.ibis()

    tables = conn.list_tables()
    print("Available tables:", tables)

    search_docs = conn.table("search_docs", database=dataset.dataset_name)
    author_name = conn.table("search_docs__author_name", database=dataset.dataset_name)

    print("search_docs columns:", search_docs.columns)
    print("search_docs__author_name columns:", author_name.columns)

    return author_name, conn, dataset, search_docs


@app.cell
def __(author_name, ibis, search_docs):
    works_with_authors = search_docs.join(
        author_name,
        search_docs._dlt_id == author_name._dlt_parent_id,
    )

    top_authors = (
        works_with_authors.filter(works_with_authors.value.notnull())
        .group_by(author_name=works_with_authors.value)
        .aggregate(book_count=works_with_authors.value.count())
        .order_by(ibis.desc("book_count"))
        .limit(10)
    )

    top_authors_df = top_authors.execute()
    return top_authors_df,


@app.cell
def __(mo, px, top_authors_df):
    fig = px.bar(
        top_authors_df,
        x="author_name",
        y="book_count",
        title="Top 10 Authors by Book Count",
    )
    fig.update_layout(xaxis_title="Author", yaxis_title="Book count")

    mo.ui.tabs(
        {
            "Top 10 Authors": fig,
            "Raw Data": top_authors_df,
        }
    )
    return