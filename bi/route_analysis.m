// AeroLens Power Query M — run in Microsoft Power BI Desktop.
// Set FilePath to your local, checked-out repository CSV full path.
// Actual 2024/2025 CAA passenger numbers are all-airline, both directions.
let
    FilePath = "C:\REPLACE\AeroLens_Advanced_v2\data\derived\route_summary.csv",
    Raw = Csv.Document(File.Contents(FilePath), [Delimiter=",", Columns=7, Encoding=65001, QuoteStyle=QuoteStyle.Csv]),
    Header = Table.PromoteHeaders(Raw, [PromoteAllScalars=true]),
    Types = Table.TransformColumnTypes(Header, {
        {"code",type text}, {"city",type text}, {"region",type text},
        {"y2024",Int64.Type}, {"y2025",Int64.Type},
        {"delta",Int64.Type}, {"growth_pct",type number}
    }),
    Guarded = Table.SelectRows(Types, each [y2024] > 0 and [y2025] > 0),
    Checked = Table.AddColumn(Guarded, "QA_DeltaCorrect", each [delta] = [y2025] - [y2024], type logical)
in
    Checked
