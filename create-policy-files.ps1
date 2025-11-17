# PowerShell script to create all Policy-as-Code files
# Run this script from the tinyllama-x directory

Write-Host "Creating Policy-as-Code files..." -ForegroundColor Green

# Create config/policies.yaml
Write-Host "Creating config/policies.yaml..."
@'
# TinyLlama-X Policy Configuration
# Runtime policies and enforcement rules

# Policy metadata
metadata:
  version: "1.0.0"
  last_updated: "2025-11-15T00:00:00Z"
  description: "TinyLlama-X runtime policies"

# Enforcement configuration
enforcement:
  mode: enforce  # enforce, audit, warn
  fail_open: false  # Allow operations if policy check fails
  log_violations: true
  alert_on_violations: true

# Container runtime policies
container:
  # Image policies
  images:
    require_signature: true
    allowed_registries:
      - ghcr.io/120git
      - docker.io/library
      - registry.k8s.io
    disallow_latest_tag: true
    scan_for_vulnerabilities: true
    max_critical_vulnerabilities: 0
    max_high_vulnerabilities: 5
  
  # Security context policies
  security_context:
    require_nonroot: true
    require_readonly_fs: true
    disallow_privilege_escalation: true
    drop_all_capabilities: true
    allowed_capabilities: []
    required_seccomp_profile: RuntimeDefault
    allow_host_network: false
    allow_host_pid: false
    allow_host_ipc: false

# Package manager policies
package_manager:
  # Operation restrictions
  operations:
    allow_install: true
    allow_remove: true
    allow_upgrade: true
    allow_downgrade: false
    require_dry_run: false  # Force dry-run for all operations
  
  # Ephemeral operations (containers only)
  ephemeral:
    allow_ephemeral_remove: false  # Allow removing packages in containers
    allow_ephemeral_install: true
    restore_on_exit: false
  
  # Restricted operations
  restricted:
    disallow_kernel_updates: true
    disallow_system_critical_packages: true
    critical_packages:
      - systemd
      - init
      - kernel
      - glibc
      - bash
  
  # Repository policies
  repositories:
    allow_third_party: false
    allowed_ppa_list: []
    require_gpg_verification: true

# Command execution policies
commands:
  # Allowed operations
  allow_list:
    enabled: false
    commands: []
  
  # Denied operations
  deny_list:
    enabled: true
    commands:
      - rm -rf /
      - dd if=/dev/zero
      - :(){ :|:& };:  # Fork bomb
      - mkfs
    patterns:
      - ".*>/dev/sd[a-z].*"  # Direct disk writes
  
  # Sudo policies
  sudo:
    allow_sudo: true
    require_password: true
    log_all_sudo: true

# Network policies
network:
  # Egress restrictions
  egress:
    allow_all: false
    allowed_destinations:
      - control-plane.tinyllamax.io
      - "*.ubuntu.com"
      - "*.debian.org"
      - "*.fedoraproject.org"
    allowed_ports:
      - 80
      - 443
      - 8000
  
  # Ingress restrictions
  ingress:
    allow_all: false
    allowed_sources: []

# Audit and compliance
audit:
  enabled: true
  log_all_commands: true
  log_policy_decisions: true
  log_config_changes: true
  retention_days: 90
  
  # Compliance frameworks
  compliance:
    cis_benchmark: true
    pci_dss: false
    hipaa: false
    soc2: true

# Feature flags for policy enforcement
features:
  enable_signature_verification: true
  enable_vulnerability_scanning: true
  enable_runtime_protection: true
  enable_network_policies: true
  enable_audit_logging: true

# Rollback configuration
rollback:
  enabled: true
  automatic: true
  max_rollback_attempts: 3
  rollback_on_failure: true
  preserve_backups: 5

# Notification configuration
notifications:
  enabled: true
  channels:
    - slack
    - email
  severity_threshold: high  # low, medium, high, critical
  
  # Notification events
  events:
    policy_violation: true
    config_change: true
    security_incident: true
    service_degraded: true
'@ | Out-File -FilePath "config\policies.yaml" -Encoding UTF8

# Create config/features.yaml
Write-Host "Creating config/features.yaml..."
@'
# TinyLlama-X Feature Flags
# Control experimental and optional features

# Core features
core:
  # AI assistant features
  ai_assistant:
    enabled: true
    model_backend: ollama  # ollama, llamacpp, fake
    intent_detection: true
    context_awareness: true
    multi_step_planning: true
  
  # Distributed features
  federation:
    enabled: true
    control_plane_url: ""  # Set via environment
    agent_daemon: true
    sync_enabled: true
    telemetry_upload: true

# UI features
ui:
  # Terminal UI
  terminal:
    enabled: true
    colored_output: true
    interactive_prompts: true
    progress_bars: true
  
  # Web UI (experimental)
  web:
    enabled: false
    port: 8080
    authentication: true
    tls: true

# Advanced features
advanced:
  # RAG (Retrieval Augmented Generation)
  rag:
    enabled: true
    embedding_model: all-MiniLM-L6-v2
    vector_store: faiss
    max_context_documents: 5
  
  # Self-healing
  self_healing:
    enabled: true
    auto_fix: true
    max_retry_attempts: 3
    notification_on_fix: true
  
  # Predictive maintenance
  predictive:
    enabled: false
    disk_space_prediction: false
    package_update_prediction: false
    anomaly_detection: false

# Container-specific features
container:
  # Docker integration
  docker:
    enabled: true
    socket_path: /var/run/docker.sock
    manage_containers: true
  
  # Kubernetes integration
  kubernetes:
    enabled: true
    in_cluster_config: true
    manage_pods: true
    operator_mode: false

# Experimental features
experimental:
  # These features are under development
  gui:
    enabled: false
    framework: electron
    auto_launch: false
  
  # Natural language shell
  nl_shell:
    enabled: false
    fuzzy_matching: false
    command_suggestions: false
  
  # Automated testing
  auto_testing:
    enabled: false
    smoke_tests: false
    integration_tests: false
  
  # Model fine-tuning
  fine_tuning:
    enabled: false
    collect_training_data: false
    periodic_retraining: false
  
  # Multi-agent collaboration
  multi_agent:
    enabled: false
    agent_discovery: false
    task_distribution: false

# Plugin system
plugins:
  enabled: false
  auto_load: false
  allowed_plugins: []
  plugin_directory: /opt/tinyllamax/plugins

# Performance features
performance:
  # Caching
  cache:
    enabled: true
    model_cache: true
    embedding_cache: true
    response_cache: false
    cache_ttl_seconds: 3600
  
  # Optimization
  optimization:
    lazy_loading: true
    batch_processing: true
    parallel_execution: true
    memory_optimization: true

# Security features
security:
  # Advanced authentication
  authentication:
    mfa: false
    oauth2: false
    ldap: false
  
  # Encryption
  encryption:
    at_rest: false
    in_transit: true
    key_rotation: false
  
  # Sandboxing
  sandbox:
    enabled: false
    container_based: false
    vm_based: false

# Observability features
observability:
  # Metrics
  metrics:
    custom_metrics: true
    business_metrics: false
  
  # Distributed tracing
  tracing:
    detailed_spans: true
    trace_sampling: true
    correlation_ids: true
  
  # Profiling
  profiling:
    enabled: false
    cpu_profiling: false
    memory_profiling: false

# Integration features
integrations:
  # CI/CD
  cicd:
    github_actions: true
    gitlab_ci: false
    jenkins: false
  
  # Monitoring
  monitoring:
    prometheus: true
    grafana: true
    datadog: false
    newrelic: false
  
  # Ticketing
  ticketing:
    jira: false
    servicenow: false
    pagerduty: false

# Developer features
developer:
  debug_mode: false
  verbose_logging: false
  api_documentation: true
  swagger_ui: true
  development_server: false
'@ | Out-File -FilePath "config\features.yaml" -Encoding UTF8

Write-Host "`nAll Policy-as-Code configuration files created successfully!" -ForegroundColor Green
Write-Host "`nNote: Large files (Makefile, docs, tools, gitops) will be created in next steps." -ForegroundColor Yellow
Write-Host "Run: git add config/ && git status" -ForegroundColor Cyan
