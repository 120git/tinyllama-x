# TinyLlama-X Global Defaults
# Default configuration values applied across all environments

# Logging configuration
logging:
  level: INFO  # DEBUG, INFO, WARNING, ERROR, CRITICAL
  format: json  # json, text
  output: stdout  # stdout, file, syslog
  file_path: /var/log/tinyllamax/tinyllamax.log
  max_size_mb: 100
  backup_count: 5
  enable_audit: true

# Telemetry configuration
telemetry:
  enabled: true
  interval_seconds: 300
  batch_size: 100
  
  # Metrics
  metrics:
    enabled: true
    exporter: prometheus  # prometheus, otlp, none
    port: 9090
    path: /metrics
  
  # Logs
  logs:
    enabled: true
    exporter: loki  # loki, otlp, none
    endpoint: http://loki:3100
  
  # Traces
  traces:
    enabled: true
    exporter: tempo  # tempo, jaeger, otlp, none
    endpoint: http://tempo:4317
    sample_rate: 0.1  # 10% sampling

# OpenTelemetry configuration
opentelemetry:
  enabled: true
  service_name: tinyllamax
  service_version: 0.1.0
  environment: production
  
  # OTLP exporter
  otlp:
    endpoint: http://otel-collector:4317
    protocol: grpc  # grpc, http/protobuf
    insecure: false
    headers: {}
    compression: gzip

# Health check configuration
health:
  enabled: true
  port: 8080
  path: /health
  checks:
    - disk_space
    - memory
    - control_plane_connectivity
  thresholds:
    disk_percent_warning: 80
    disk_percent_critical: 90
    memory_percent_warning: 85
    memory_percent_critical: 95

# Heartbeat configuration
heartbeat:
  interval_seconds: 60
  timeout_seconds: 30
  retry_count: 3
  backoff_multiplier: 2

# Sync configuration
sync:
  interval_seconds: 300
  timeout_seconds: 120
  verify_signatures: true
  max_retries: 5

# Performance configuration
performance:
  max_workers: 4
  connection_pool_size: 10
  request_timeout_seconds: 30
  keep_alive: true

# Security defaults
security:
  tls_version: "1.3"
  cipher_suites:
    - TLS_AES_256_GCM_SHA384
    - TLS_AES_128_GCM_SHA256
    - TLS_CHACHA20_POLY1305_SHA256
  verify_certificates: true
  mutual_tls: false  # Enable in production

# Model configuration
model:
  backend: ollama  # ollama, llamacpp, fake
  name: tinyllama:1.1b
  temperature: 0.7
  max_tokens: 512
  cache_dir: /var/cache/tinyllamax/models
  auto_update: true

# Package manager configuration
package_manager:
  allowed_managers:
    - apt
    - dnf
    - pacman
    - zypper
  default_dry_run: false
  require_confirmation: true
  timeout_seconds: 600

# Rate limiting
rate_limiting:
  enabled: true
  requests_per_minute: 60
  burst: 10

# Retention policies
retention:
  metrics_days: 30
  logs_days: 14
  traces_days: 7
  telemetry_batch_max_age_hours: 24
