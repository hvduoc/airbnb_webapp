#!/bin/bash
# Bash Script để ghi log từng phase phát triển
# log-phase.sh

set -e

# Cấu hình mặc định
BRAIN_DIR="./.brain"
LOG_DIR="$BRAIN_DIR/LOG/phases"
TASKS_FILE="$BRAIN_DIR/ACTIVE_TASKS.json"

# Functions
show_help() {
    cat << EOF
Usage: $0 -p PHASE_NUMBER -n PHASE_NAME [OPTIONS]

Options:
    -p, --phase NUMBER      Phase number (required)
    -n, --name NAME         Phase name (required)
    -d, --description DESC  Phase description
    -s, --start DATE        Start date (YYYY-MM-DD HH:MM)
    -e, --end DATE          End date (YYYY-MM-DD HH:MM)
    -f, --files FILES       Comma-separated list of changed files
    -t, --tasks TASKS       Comma-separated list of updated tasks
    --difficulties TEXT     Difficulties encountered
    --next-steps TEXT       Next steps suggestions
    -i, --interactive       Interactive mode
    -h, --help             Show this help

Examples:
    $0 -p 8 -n "Log Management" -i
    $0 -p 8 -n "Log Management" -d "Phase 8 implementation" -f "script1.sh,script2.py"
EOF
}

log_info() {
    echo -e "\033[32m$1\033[0m"
}

log_warn() {
    echo -e "\033[33m$1\033[0m"
}

log_error() {
    echo -e "\033[31m$1\033[0m"
}

get_git_changes() {
    # Try to get changes from git
    if command -v git >/dev/null 2>&1 && git rev-parse --git-dir >/dev/null 2>&1; then
        git diff --name-only HEAD~1 2>/dev/null || echo ""
    else
        # Fallback: find recently modified files
        find . -type f -mtime -1 -not -path "./.git/*" -not -path "./node_modules/*" -not -name "*.log" -not -name "*.tmp" 2>/dev/null | sed 's|^\./||' | head -20
    fi
}

get_task_stats() {
    if [[ ! -f "$TASKS_FILE" ]]; then
        echo '{"total":0,"completed":0,"in_progress":0,"pending":0,"blocked":0,"percentage":0}'
        return
    fi
    
    # Sử dụng jq nếu có, không thì fallback
    if command -v jq >/dev/null 2>&1; then
        local total=$(jq '[.phases[].tasks[]] | length' "$TASKS_FILE" 2>/dev/null || echo 0)
        local completed=$(jq '[.phases[].tasks[] | select(.status == "completed")] | length' "$TASKS_FILE" 2>/dev/null || echo 0)
        local in_progress=$(jq '[.phases[].tasks[] | select(.status == "in_progress")] | length' "$TASKS_FILE" 2>/dev/null || echo 0)
        local pending=$(jq '[.phases[].tasks[] | select(.status == "pending")] | length' "$TASKS_FILE" 2>/dev/null || echo 0)
        local blocked=$(jq '[.phases[].tasks[] | select(.status == "blocked")] | length' "$TASKS_FILE" 2>/dev/null || echo 0)
        
        local percentage=0
        if [[ $total -gt 0 ]]; then
            percentage=$(echo "scale=1; $completed * 100 / $total" | bc 2>/dev/null || echo 0)
        fi
        
        echo "{\"total\":$total,\"completed\":$completed,\"in_progress\":$in_progress,\"pending\":$pending,\"blocked\":$blocked,\"percentage\":$percentage}"
    else
        # Simple fallback without jq
        echo '{"total":0,"completed":0,"in_progress":0,"pending":0,"blocked":0,"percentage":0}'
    fi
}

backup_tasks_file() {
    if [[ -f "$TASKS_FILE" ]]; then
        local timestamp=$(date +"%Y%m%d-%H%M%S")
        local backup_file="$LOG_DIR/ACTIVE_TASKS_backup_$timestamp.json"
        cp "$TASKS_FILE" "$backup_file"
        log_info "✅ Backed up tasks to: $backup_file"
    fi
}

interactive_input() {
    log_info "📝 Interactive Phase Log Creation"
    echo "================================="
    echo ""
    
    if [[ -z "$DESCRIPTION" ]]; then
        read -p "Mô tả phase (Enter để bỏ qua): " DESCRIPTION
    fi
    
    if [[ -z "$START_DATE" ]]; then
        local default_start=$(date -d "4 hours ago" +"%Y-%m-%d %H:%M" 2>/dev/null || date +"%Y-%m-%d %H:%M")
        read -p "Thời gian bắt đầu [$default_start]: " input_start
        START_DATE=${input_start:-$default_start}
    fi
    
    if [[ -z "$END_DATE" ]]; then
        local default_end=$(date +"%Y-%m-%d %H:%M")
        read -p "Thời gian kết thúc [$default_end]: " input_end
        END_DATE=${input_end:-$default_end}
    fi
    
    if [[ -z "$DIFFICULTIES" ]]; then
        read -p "Khó khăn gặp phải (Enter để bỏ qua): " DIFFICULTIES
    fi
    
    if [[ -z "$NEXT_STEPS" ]]; then
        read -p "Gợi ý bước tiếp theo (Enter để bỏ qua): " NEXT_STEPS
    fi
    
    # Show detected file changes
    echo ""
    log_warn "📁 File changes detected:"
    local detected_files=$(get_git_changes)
    if [[ -n "$detected_files" ]]; then
        echo "$detected_files" | while read -r file; do
            [[ -n "$file" ]] && echo "   - $file"
        done
        read -p "Sử dụng danh sách file này? (Y/n): " confirm_files
        if [[ "$confirm_files" != "n" && "$confirm_files" != "N" ]]; then
            FILES_CHANGED="$detected_files"
        fi
    fi
    
    if [[ -z "$FILES_CHANGED" ]]; then
        echo "Nhập danh sách file thay đổi (mỗi file 1 dòng, Enter trống để kết thúc):"
        local file_list=""
        while true; do
            read -p "File: " file
            [[ -z "$file" ]] && break
            file_list="$file_list$file"$'\n'
        done
        FILES_CHANGED="$file_list"
    fi
}

create_phase_log() {
    # Tạo thư mục nếu chưa có
    mkdir -p "$LOG_DIR"
    
    # Backup tasks file
    backup_tasks_file
    
    # Lấy thống kê tasks
    local task_stats=$(get_task_stats)
    local total=$(echo "$task_stats" | grep -o '"total":[0-9]*' | cut -d':' -f2 || echo 0)
    local completed=$(echo "$task_stats" | grep -o '"completed":[0-9]*' | cut -d':' -f2 || echo 0)
    local in_progress=$(echo "$task_stats" | grep -o '"in_progress":[0-9]*' | cut -d':' -f2 || echo 0)
    local pending=$(echo "$task_stats" | grep -o '"pending":[0-9]*' | cut -d':' -f2 || echo 0)
    local blocked=$(echo "$task_stats" | grep -o '"blocked":[0-9]*' | cut -d':' -f2 || echo 0)
    local percentage=$(echo "$task_stats" | grep -o '"percentage":[0-9.]*' | cut -d':' -f2 || echo 0)
    
    # Tạo file log
    local phase_file="$LOG_DIR/PHASE-$(printf "%02d" "$PHASE_NUMBER").md"
    local current_time=$(date +"%Y-%m-%d %H:%M:%S")
    local git_commit=$(git rev-parse --short HEAD 2>/dev/null || echo "N/A")
    local git_branch=$(git branch --show-current 2>/dev/null || echo "N/A")
    
    cat > "$phase_file" << EOF
# PHASE-$(printf "%02d" "$PHASE_NUMBER"): $PHASE_NAME

## ⏰ Thời gian
- **Bắt đầu:** ${START_DATE:-$(date -d "2 hours ago" +"%Y-%m-%d %H:%M" 2>/dev/null || date +"%Y-%m-%d %H:%M")}
- **Kết thúc:** ${END_DATE:-$(date +"%Y-%m-%d %H:%M")}
- **Tạo log:** $current_time

## 🎯 Mục tiêu
${DESCRIPTION:-"Phát triển và hoàn thiện tính năng $PHASE_NAME"}

## 📊 Kết quả

### Files đã tạo/sửa:
EOF

    if [[ -n "$FILES_CHANGED" ]]; then
        echo "$FILES_CHANGED" | while IFS= read -r file; do
            [[ -n "$file" ]] && echo "- \`$file\`" >> "$phase_file"
        done
    else
        echo "- *(Không có file nào được ghi nhận)*" >> "$phase_file"
    fi

    cat >> "$phase_file" << EOF

### Tasks được cập nhật:
EOF

    if [[ -n "$TASKS_UPDATED" ]]; then
        echo "$TASKS_UPDATED" | tr ',' '\n' | while IFS= read -r task; do
            [[ -n "$task" ]] && echo "- $task" >> "$phase_file"
        done
    else
        echo "- *(Sẽ cập nhật thủ công)*" >> "$phase_file"
    fi

    cat >> "$phase_file" << EOF

### 📈 Thống kê tiến độ:
- **Tổng số task:** $total
- **Hoàn thành:** $completed/$total
- **Đang thực hiện:** $in_progress
- **Chờ xử lý:** $pending
- **Bị chặn:** $blocked
- **Tỷ lệ hoàn thành:** $percentage%

## 🚫 Khó khăn
${DIFFICULTIES:-"Không có khó khăn đáng kể"}

## 💡 Gợi ý tiếp theo
${NEXT_STEPS:-"Tiếp tục sang Phase $(printf "%02d" $((PHASE_NUMBER + 1))): Tối ưu hóa và kiểm thử"}

## 🔧 Technical Notes
- **Git commit:** $git_commit
- **Branch:** $git_branch
- **Environment:** $(uname -s) $(uname -m)
- **Log generated:** $current_time

---
*Log này được tạo tự động bởi log-phase.sh*
EOF

    log_info ""
    log_info "✅ Phase log created successfully!"
    echo "📁 Location: $phase_file"
    echo ""
    
    # Hiển thị summary
    log_info "📊 Phase Summary:"
    echo "   Phase: PHASE-$(printf "%02d" "$PHASE_NUMBER") - $PHASE_NAME"
    echo "   Files changed: $(echo "$FILES_CHANGED" | wc -l)"
    echo "   Progress: $completed/$total tasks ($percentage%)"
    echo ""
}

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -p|--phase)
            PHASE_NUMBER="$2"
            shift 2
            ;;
        -n|--name)
            PHASE_NAME="$2"
            shift 2
            ;;
        -d|--description)
            DESCRIPTION="$2"
            shift 2
            ;;
        -s|--start)
            START_DATE="$2"
            shift 2
            ;;
        -e|--end)
            END_DATE="$2"
            shift 2
            ;;
        -f|--files)
            FILES_CHANGED=$(echo "$2" | tr ',' '\n')
            shift 2
            ;;
        -t|--tasks)
            TASKS_UPDATED="$2"
            shift 2
            ;;
        --difficulties)
            DIFFICULTIES="$2"
            shift 2
            ;;
        --next-steps)
            NEXT_STEPS="$2"
            shift 2
            ;;
        -i|--interactive)
            INTERACTIVE=true
            shift
            ;;
        -h|--help)
            show_help
            exit 0
            ;;
        *)
            log_error "Unknown option: $1"
            show_help
            exit 1
            ;;
    esac
done

# Main execution
log_info "🚀 Phase Log Generator"
echo "====================="
echo ""

# Validate inputs
if [[ -z "$PHASE_NUMBER" ]] || [[ ! "$PHASE_NUMBER" =~ ^[0-9]+$ ]]; then
    log_error "Phase number is required and must be numeric"
    show_help
    exit 1
fi

if [[ -z "$PHASE_NAME" ]]; then
    log_error "Phase name is required"
    show_help
    exit 1
fi

# Interactive mode
if [[ "$INTERACTIVE" == true ]]; then
    interactive_input
else
    # Auto-detect file changes if not provided
    if [[ -z "$FILES_CHANGED" ]]; then
        log_warn "🔍 Auto-detecting file changes..."
        FILES_CHANGED=$(get_git_changes)
    fi
    
    # Set default dates if not provided
    if [[ -z "$START_DATE" ]]; then
        START_DATE=$(date -d "2 hours ago" +"%Y-%m-%d %H:%M" 2>/dev/null || date +"%Y-%m-%d %H:%M")
    fi
    if [[ -z "$END_DATE" ]]; then
        END_DATE=$(date +"%Y-%m-%d %H:%M")
    fi
fi

# Create the log
create_phase_log

log_info "🎉 Phase logging completed successfully!"