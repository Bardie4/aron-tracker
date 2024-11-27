use actix_cors::Cors;
use actix_web::{web, App, HttpServer, Responder};
use polars::prelude::*;
use reqwest;
use serde_json::json;

// Custom function to handle CSV download and error conversion
async fn download_csv(url: &str) -> Result<String> {
    let response = reqwest::get(url)
        .await
        .map_err(|e| PolarsError::from(anyhow::anyhow!(e)))?;
    response
        .text()
        .await
        .map_err(|e| PolarsError::from(anyhow::anyhow!(e)))
}

// New endpoint to fetch CSV and calculate TotalStats
async fn fetch_and_calculate() -> impl Responder {
    let url = "https://docs.google.com/spreadsheets/d/1-NblbDmCxDEi5_BCSeVwzzMxZza1Mdbbv8HIPz8XXBI/export?format=csv";

    // Download CSV data
    let response = download_csv(url).await.unwrap();

    // Create a DataFrame from the CSV content
    let df = CsvReader::new(std::io::Cursor::new(response.as_bytes()))
        .has_header(true)
        .finish()
        .unwrap();

    // Calculate TotalStats fields
    let total_today: i32 = df["Flaske"].sum().unwrap();
    let n_feeds_today: usize = df.filter(&df["Dato"].is_not_null()).unwrap().height();
    let largest_meal: i32 = df["Flaske"].max().unwrap();

    // Create a JSON response
    let result = json!({
        "total_today": total_today,
        "n_feeds_today": n_feeds_today,
        "largest_meal": largest_meal,
    });

    println!("{:?}", result);

    web::Json(result)
}

#[actix_web::main]
async fn main() -> std::io::Result<()> {
    HttpServer::new(|| {
        App::new()
            .wrap(
                Cors::default()
                    .allowed_origin("http://localhost:3000")
                    .allowed_methods(vec!["GET", "POST"])
                    .allowed_headers(vec!["Content-Type"])
                    .max_age(3600),
            )
            // ... existing routes ...
            .route("/fetch_stats", web::get().to(fetch_and_calculate)) // New route
    })
    .bind("127.0.0.1:8080")?
    .run()
    .await
}
