# 🏁 SESSION END PROMPT  

**Copy-paste this to properly close work session:**

---

📝 SESSION END

**🚨 EVOLVED: Sử dụng .brain/LOG/daily/ system thay thế!**

---

**⚡ MODERN SESSION END:**

🎯 **Simplified End Process:**

1. **Manual Update**: Update .brain/LOG/daily/[today].md với progress
2. **Commit Changes**: git commit với clear message  
3. **Update Tasks**: Mark progress trong .brain/ACTIVE_TASKS.json nếu cần
4. **Next Session**: Set priority trong .brain/CONTEXT_INDEX.md

**💡 NO MORE MANUAL PROMPTS:**
- Brain system tracks progress automatically
- Daily logs replace manual session reports
- Context preserved trong structured files
- AI gets context từ CONTEXT_INDEX.md next session

**🔄 MIGRATION:**
- Old: Manual handoff reports
- New: Structured daily logging + brain files
- Result: Better continuity, less manual work

**👤 CHO NGƯỜI DÙNG:**
Thay vì paste prompt này:
```
1. Update daily log manually: .brain/LOG/daily/2025-09-25.md
2. Commit work: git commit -m "feat: completed TASK-001"  
3. Ready for next session!
```

---

## 📋 Expected AI Response Format:

```
🏁 SESSION HANDOFF REPORT
Session Date: [YYYY-MM-DD]
AI Agent: [Name/Version]  
Duration: [X hours Y minutes]
Focus Area: [Main objective]

✅ COMPLETED:
- [Specific achievements with impact]
- [Files modified/created]
- [Problems solved]

🔄 IN PROGRESS:  
- [Tasks started but not finished]
- [Current state/next steps]

🚨 CRITICAL ISSUES:
- [Blocking problems for next session]
- [Bugs discovered]
- [Dependencies needed]

📋 NEXT SESSION PRIORITIES:
1. [Most urgent task - with time estimate]
2. [Secondary task]  
3. [Optional improvements]

🎯 CONTEXT UPDATED:
- ✅ PROJECT_STATE.md metrics refreshed
- ✅ ACTIVE_TASKS.json progress updated
- ✅ DAILY_LOG.md session logged
- ✅ Files committed/organized

💡 KEY INSIGHTS:
- [Important learnings for future sessions]
- [Architecture decisions made]
- [Patterns to follow/avoid]

🔗 HANDOFF COMPLETE - READY FOR NEXT AI
```

## 🎯 Purpose:
- **Knowledge Preservation**: No context loss between sessions
- **Priority Clarity**: Next AI knows exactly what to work on
- **Progress Tracking**: Maintain project momentum
- **Quality Assurance**: Document decisions and learnings

## ⚡ Usage:
1. Use when ending any work session
2. Wait for AI to update all context files
3. Review the handoff report for completeness
4. Next session will have perfect continuity

## 🔄 Integration with Start:
- SESSION_END updates → SESSION_START reads → Perfect continuity
- Each session builds on previous session's handoff
- No repeated work or forgotten progress

*File: .prompts/03_SESSION_END.md*