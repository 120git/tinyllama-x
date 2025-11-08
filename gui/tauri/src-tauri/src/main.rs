// Prevents additional console window on Windows in release
#![cfg_attr(not(debug_assertions), windows_subsystem = "windows")]

// Tauri commands go here
// These will be callable from the frontend

#[tauri::command]
fn greet(name: &str) -> String {
    format!("Hello, {}! Welcome to TinyLlama-X", name)
}

fn main() {
    tauri::Builder::default()
        .invoke_handler(tauri::generate_handler![greet])
        .run(tauri::generate_context!())
        .expect("error while running tauri application");
}

// TODO: Implement actual integration with TinyLlama-X
// Options:
// 1. HTTP bridge to FastAPI server running presenter
// 2. Shell commands via tauri-plugin-shell with strict allowlist
// 3. Native Rust bindings to Python (PyO3)
//
// Example command structure:
//
// #[tauri::command]
// async fn classify_intent(text: String) -> Result<String, String> {
//     // Call Python bridge or execute command
//     // Return JSON result
// }
//
// #[tauri::command]
// async fn simulate_plan(plan_id: String) -> Result<String, String> {
//     // Execute simulation
// }
//
// #[tauri::command]
// async fn execute_plan(plan_id: String) -> Result<String, String> {
//     // Execute real command with confirmation
// }
