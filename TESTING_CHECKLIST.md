# Testing Checklist - Phase 2

## 🧪 Testing Order

### 1. Initial Setup Check
- [ ] App starts without errors
- [ ] Login page loads
- [ ] Can see login form

### 2. Employee Testing
**Login Credentials:** (Use your existing employee account)

#### Test A: Task Completion & Status
- [ ] Login as employee
- [ ] View "My Tasks" 
- [ ] Complete a task
- [ ] Verify completion_timestamp is recorded
- [ ] Check if status shows correctly

#### Test B: Excuse Submission & Scoring
**High-Quality Excuse:**
```
Server crashed at 10am due to memory leak. I immediately contacted IT, 
restarted the service, and documented the issue. I will set up monitoring 
alerts to prevent this in future.
```
- [ ] Submit above excuse
- [ ] Expected: **90-100% authenticity**
- [ ] Expected: Category = **Technical** 🔧
- [ ] Verify category icon displays
- [ ] Check avoidance score = 100 - authenticity

**Low-Quality Excuse:**
```
Something came up.
```
- [ ] Submit above excuse
- [ ] Expected: **0-20% authenticity**
- [ ] Expected: Category = **Other** ❓

#### Test C: Recent Submissions Panel
- [ ] Go to Dashboard
- [ ] Scroll to bottom
- [ ] See "📝 Recent Excuse Submissions" section
- [ ] Should show your 2 submissions
- [ ] Check trend indicator (↑ or ↓)
- [ ] Verify categories display

### 3. Manager Testing
**Login as Manager/Admin**

#### Test D: Manager Insights Panel
- [ ] Login as manager/admin
- [ ] Navigate to Analytics page
- [ ] Scroll to bottom
- [ ] See "🎯 Employee Risk Insights" section
- [ ] If employees have 3+ delays → shows high-risk warning
- [ ] If no high-risk → shows success message

### 4. Status Badge Testing
- [ ] Create task with 60 min estimate
- [ ] Complete after 90 min (takes longer)
- [ ] Verify badge shows: **🟠 Completed Over Time**
- [ ] Color should be orange (#fb923c)

### 5. Formula Verification
- [ ] Same excuse submitted twice = same score
- [ ] Different excuses = different scores
- [ ] High quality > 80%, Low quality < 20%
- [ ] All scores are whole numbers (0-100)

## ✅ Success Criteria

All tests pass when:
- ✅ No Python errors in terminal
- ✅ All UI components visible
- ✅ Scores are deterministic
- ✅ Trend indicators work
- ✅ Categories classified correctly
- ✅ Manager insights show (if applicable)

## 🚨 Common Issues

**If Recent Submissions doesn't show:**
- Check if you've submitted any excuses
- Verify `get_user_delay_history()` function exists
- Check database has delay records

**If Manager Insights is empty:**
- This is correct if no employees have 3+ delays
- Create delays to test

**If scores are wrong:**
- Verify `scoring_engine.py` is being imported
- Check `service_submit_delay()` uses formulas
- Not using old AI-based scoring

## 📝 Report Results

After testing, note:
- Which tests passed ✅
- Which tests failed ❌
- Any error messages
- Screenshots of UI components
