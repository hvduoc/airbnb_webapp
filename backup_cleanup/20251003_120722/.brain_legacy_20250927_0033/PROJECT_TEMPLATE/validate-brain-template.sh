#!/bin/bash
# 🔍 VALIDATE BRAIN TEMPLATE - Bash Script
# Mục tiêu: Kiểm tra brain system sau khi setup từ template

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
CYAN='\033[0;36m'
GRAY='\033[0;37m'
WHITE='\033[1;37m'
NC='\033[0m'

success() { echo -e "${GREEN}✅ $1${NC}"; }
warning() { echo -e "${YELLOW}⚠️ $1${NC}"; }
error() { echo -e "${RED}❌ $1${NC}"; }
info() { echo -e "${CYAN}ℹ️ $1${NC}"; }

# Default brain path
BRAIN_PATH=".brain"

# Parse arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        --brain-path)
            BRAIN_PATH="$2"
            shift 2
            ;;
        *)
            error "Unknown parameter: $1"
            echo "Usage: $0 [--brain-path PATH]"
            exit 1
            ;;
    esac
done

info "🔍 BẮT ĐẦU VALIDATION BRAIN TEMPLATE SYSTEM"
info "📁 Kiểm tra thư mục: $BRAIN_PATH"

# Tracking results
FILES_CHECKED=0
PASSED=0
WARNINGS=0
FAILED=0
ISSUES=()

add_result() {
    local status=$1
    local message=$2
    local details=$3
    
    ((FILES_CHECKED++))
    
    case $status in
        "PASS")
            ((PASSED++))
            success "$message"
            ;;
        "WARN")
            ((WARNINGS++))
            warning "$message"
            if [ -n "$details" ]; then
                ISSUES+=("WARNING: $message - $details")
            fi
            ;;
        "FAIL")
            ((FAILED++))
            error "$message"
            ISSUES+=("FAILED: $message - $details")
            ;;
    esac
}

info ""
info "📋 **KIỂM TRA CẤU TRÚC THU MỤC**"

# Kiểm tra brain directory
if [ ! -d "$BRAIN_PATH" ]; then
    add_result "FAIL" "Brain directory không tồn tại: $BRAIN_PATH" "Run create-brain-from-template script first"
    info "🚨 VALIDATION STOPPED - Không tìm thấy brain system"
    exit 1
fi

add_result "PASS" "Brain directory tồn tại: $BRAIN_PATH"

# Kiểm tra required directories
REQUIRED_DIRS=("tasks" "context" "logs/daily")
for dir in "${REQUIRED_DIRS[@]}"; do
    if [ -d "$BRAIN_PATH/$dir" ]; then
        add_result "PASS" "Thư mục required: $dir"
    else
        add_result "FAIL" "Thiếu thư mục: $dir" "Create missing directory structure"
    fi
done

info ""
info "📄 **KIỂM TRA FILES CỐT LÕI**"

# Core files check
declare -A CORE_FILES=(
    ["SCOPE.md"]="Project scope definition"
    ["tasks/ACTIVE_TASKS.json"]="Active tasks tracking"
    ["context/CONTEXT_INDEX.md"]="Context index"
)

for file in "${!CORE_FILES[@]}"; do
    description="${CORE_FILES[$file]}"
    if [ -f "$BRAIN_PATH/$file" ]; then
        add_result "PASS" "File tồn tại: $file ($description)"
    else
        add_result "FAIL" "Thiếu file: $file" "$description"
    fi
done

info ""
info "🔧 **KIỂM TRA JSON SYNTAX**"

# JSON syntax validation
JSON_PATH="$BRAIN_PATH/tasks/ACTIVE_TASKS.json"
if [ -f "$JSON_PATH" ]; then
    if python3 -m json.tool "$JSON_PATH" > /dev/null 2>&1 || jq empty "$JSON_PATH" > /dev/null 2>&1; then
        add_result "PASS" "JSON syntax hợp lệ: ACTIVE_TASKS.json"
        
        # Check for required JSON fields
        if command -v jq >/dev/null 2>&1; then
            if jq -e '.project' "$JSON_PATH" > /dev/null 2>&1; then
                add_result "PASS" "JSON có project metadata"
            else
                add_result "WARN" "JSON thiếu project metadata" "Add project info to JSON"
            fi
            
            TASK_COUNT=$(jq '.active_tasks | length' "$JSON_PATH" 2>/dev/null || echo 0)
            if [ "$TASK_COUNT" -gt 0 ]; then
                add_result "PASS" "JSON có active tasks ($TASK_COUNT tasks)"
            else
                add_result "WARN" "JSON không có active tasks" "Add initial tasks to get started"
            fi
        fi
        
    else
        add_result "FAIL" "JSON syntax không hợp lệ: ACTIVE_TASKS.json" "Fix JSON syntax errors"
    fi
else
    add_result "FAIL" "Không tìm thấy ACTIVE_TASKS.json" "Create tasks file"
fi

info ""
info "🏷️ **KIỂM TRA PLACEHOLDERS**"

# Check for remaining placeholders
FILES_TO_CHECK=("SCOPE.md" "DOMAIN_MAP.md" "README.md" "context/CONTEXT_INDEX.md")

for file in "${FILES_TO_CHECK[@]}"; do
    file_path="$BRAIN_PATH/$file"
    if [ -f "$file_path" ]; then
        placeholder_count=$(grep -o '{{[^}]*}}' "$file_path" 2>/dev/null | wc -l)
        if [ "$placeholder_count" -eq 0 ]; then
            add_result "PASS" "Không còn placeholder: $file"
        else
            placeholders=$(grep -o '{{[^}]*}}' "$file_path" 2>/dev/null | head -3 | tr '\n' ', ' | sed 's/,$//')
            add_result "WARN" "Còn $placeholder_count placeholder trong: $file" "Placeholders: $placeholders"
        fi
    fi
done

info ""
info "📅 **KIỂM TRA LOGS**"

# Daily log check
TODAY=$(date +%Y-%m-%d)
TODAY_LOG_PATH="$BRAIN_PATH/logs/daily/$TODAY.md"

if [ -f "$TODAY_LOG_PATH" ]; then
    add_result "PASS" "Daily log tồn tại: $TODAY.md"
else
    add_result "WARN" "Chưa có daily log hôm nay: $TODAY.md" "Create daily log entry"
fi

info ""
info "🎯 **KẾT QUẢ VALIDATION**"

# Display results table
echo -e "${GRAY}┌─────────────────────────────────────────────┐${NC}"
echo -e "${GRAY}│${WHITE}              VALIDATION SUMMARY              ${GRAY}│${NC}"
echo -e "${GRAY}├─────────────────────────────────────────────┤${NC}"

PASS_COLOR=${GREEN}; [ $PASSED -eq 0 ] && PASS_COLOR=${GRAY}
WARN_COLOR=${YELLOW}; [ $WARNINGS -eq 0 ] && WARN_COLOR=${GRAY}
FAIL_COLOR=${RED}; [ $FAILED -eq 0 ] && FAIL_COLOR=${GRAY}

printf "${GRAY}│ ${PASS_COLOR}✅ PASSED: %2d${GRAY} │ ${WARN_COLOR}⚠️ WARNINGS: %2d${GRAY} │ ${FAIL_COLOR}❌ FAILED: %2d${GRAY} │${NC}\n" $PASSED $WARNINGS $FAILED
echo -e "${GRAY}└─────────────────────────────────────────────┘${NC}"

# Overall status
if [ $FAILED -gt 0 ]; then
    OVERALL_STATUS="FAILED"
    error "❌ BRAIN TEMPLATE VALIDATION FAILED"
    info "Cần khắc phục lỗi trước khi sử dụng system."
elif [ $WARNINGS -gt 0 ]; then
    OVERALL_STATUS="WARNINGS"
    warning "⚠️ BRAIN TEMPLATE CÓ WARNINGS"
    info "System có thể dùng được nhưng nên khắc phục warnings."
else
    OVERALL_STATUS="PASSED"
    success "🎉 BRAIN TEMPLATE VALIDATION PASSED!"
    info "Brain system đã sẵn sàng sử dụng."
fi

# Show issues if any
if [ ${#ISSUES[@]} -gt 0 ]; then
    info ""
    info "🔧 **ISSUES CẦN KHẮC PHỤC**:"
    for issue in "${ISSUES[@]}"; do
        echo -e "  ${YELLOW}• $issue${NC}"
    done
fi

info ""
info "📊 Tổng số items kiểm tra: $FILES_CHECKED"

# Exit with appropriate code
[ "$OVERALL_STATUS" = "FAILED" ] && exit 1 || exit 0