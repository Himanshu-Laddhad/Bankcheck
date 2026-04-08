# BankCheck Dashboard - User Guide

## 🚀 Getting Started

### Quick Start (30 Seconds)

1. **Open the app**: Visit `http://localhost:8501` after running `streamlit run main.py`
2. **Click a Quick Pick button**:
   - 💰 Best Savings → See top 3 high-yield savings accounts
   - 🏠 Best Mortgage → Find lenders with highest approval rates
   - 💳 Best Credit Card → Discover lowest APR cards
3. **View results instantly** with medal rankings (🥇🥈🥉)

### For Deeper Analysis (5-10 Minutes)

1. **Use the Sidebar** to select specific banks you want to compare
2. **Navigate tabs** to explore different aspects:
   - Overview: Quick insights and calculator
   - Rate Intel: Deep dive into APY/APR data
   - Complaints: Customer service quality
   - Mortgage: Lending performance
   - Safety: Financial health and grades
3. **Try the interactive tools** (calculator, quiz) for personalized insights

---

## 📊 Feature Guide

### 1. Hero Section & Quick Picks

**What it does**: Instantly shows top banks for common needs

**How to use**:
1. On the Overview page, you'll see 3 large buttons
2. Click any button to see top 3 recommendations
3. Results show with medal icons (🥇🥈🥉) and key metrics
4. Compare rates vs. national averages

**Best for**: First-time visitors wanting quick answers

---

### 2. Savings Calculator

**What it does**: Shows how much more you could earn by switching banks

**How to use**:
1. Scroll to the "How Much More Could You Earn?" section
2. Adjust the slider for your savings balance ($1k - $100k)
3. Select your current bank from dropdown
4. Choose a new bank to switch to
5. See instant results:
   - Annual earnings difference
   - 5-year projection
   - 10-year projection
   - Visual comparison chart

**Example**:
```
Balance: $10,000
Current: Chase (0.01% APY)
Switch to: Ally (4.75% APY)
Result: You'd earn $473 MORE per year
        $4,730 over 10 years!
```

**Best for**: Understanding real dollar impact of switching banks

---

### 3. Bank Matcher Quiz

**What it does**: Recommends banks based on your preferences

**How to use**:
1. Find "Find Your Ideal Bank in 4 Questions"
2. Answer 4 quick questions:
   - **Q1**: What matters most? (rates, fees, service, branches)
   - **Q2**: How much will you save? ($0-$100k+)
   - **Q3**: Need physical branches? (yes/no/doesn't matter)
   - **Q4**: Which products? (checking, savings, cards, etc.)
3. Click "Show My Matches"
4. View your top 3 personalized recommendations

**Example Results**:
```
For "Highest savings rates" + "$25k-$100k":
1. 🏆 Ally Bank - 4.75% APY - "Best overall rate"
2. ⭐ Synchrony - 4.75% APY - "Competitive online rate"
3. ✨ Marcus - 4.50% APY - "Strong brand, great rate"
```

**Best for**: Users unsure which bank fits their needs

---

### 4. Live Rankings Leaderboard

**What it does**: Shows real-time top performers

**How to use**:
1. Located on Overview page
2. Shows top 5 banks by savings APY
3. Medal icons indicate ranking
4. "Hot" badge for #1 performer
5. Updated when you refresh data

**Format**:
```
🥇 1. Ally Bank          4.75% APY ⚡ Hot
🥈 2. Synchrony Bank     4.75% APY
🥉 3. Goldman Sachs      4.50% APY
🔸 4. American Express   4.30% APY
🔸 5. Discover           4.25% APY
```

**Best for**: Quick scanning of top options

---

### 5. Animated Score Cards

**What it does**: Shows comprehensive A-F grades with visual flair

**How to use**:
1. Navigate to Overview or Safety & Scores tabs
2. View cards for each selected bank
3. Cards show:
   - Overall grade (A+ to F)
   - Animated progress bar
   - Four component scores (Rate, Complaints, Safety, Fairness)
   - Achievement badges (automatically awarded)
   - Rank indicator (#1, #2, etc.)
   - Verdict summary

**Achievement Badges**:
- 🏆 **Rate Leader**: 90+ rate score
- 💎 **Customer Favorite**: 85+ complaint score
- 🛡️ **Safety Champion**: 90+ safety score
- ⭐ **Top Pick**: 85+ overall score

**Color Coding**:
- **Green border**: A grades (excellent)
- **Blue border**: B grades (good)
- **Orange border**: C grades (average)
- **Red border**: D-F grades (poor)

**Best for**: Understanding overall bank quality at a glance

---

### 6. Interactive Charts

**Features**:
- **Hover tooltips**: Shows exact values on mouse over
- **Zoom**: Click and drag to zoom into specific ranges
- **Pan**: Drag chart to move view
- **Range selector**: Click buttons for 3m, 6m, 1y, All time views
- **Legend toggle**: Click legend items to show/hide data series
- **Download**: Camera icon to save chart as PNG

**Chart Types**:
1. **Bar Charts**: Compare values across banks
2. **Line Charts**: Track trends over time
3. **Heatmaps**: See intensity of complaints by product
4. **Gauge Charts**: Visual score indicators
5. **Bubble Charts**: Multi-dimensional comparison

**Best for**: Detailed data exploration

---

## 🎯 Common Use Cases

### Use Case 1: "I want the best savings account"

**Steps**:
1. Click **💰 Best Savings** quick pick button
2. See top 3 instantly ranked by APY
3. Use **Savings Calculator** to see earnings difference
4. Navigate to **Rate Intelligence** tab for full comparison
5. Check **Safety & Scores** to verify bank is financially sound

**Expected Time**: 2-3 minutes

---

### Use Case 2: "I'm unhappy with my current bank"

**Steps**:
1. Take the **Bank Matcher Quiz** (4 questions)
2. View personalized recommendations
3. Compare your current bank vs. recommendations in sidebar
4. Check **Complaint Intelligence** to see customer service quality
5. Use **Calculator** to see financial impact of switching

**Expected Time**: 5-7 minutes

---

### Use Case 3: "I need a mortgage"

**Steps**:
1. Navigate to **Mortgage & Lending** tab
2. View approval rates for major lenders
3. Check interest rates offered
4. See denial reasons (understand what matters)
5. Select top performers in sidebar for detailed comparison

**Expected Time**: 3-5 minutes

---

### Use Case 4: "Which banks should I avoid?"

**Steps**:
1. Go to **Overview** → Scroll to scorecards
2. Look for **F-grade** banks (red border)
3. Check **Complaint Intelligence** → Resolution rates
4. View **Rate Intelligence** → See who pays worst rates
5. Avoid banks with:
   - F grades
   - <5% relief rates
   - <0.50% savings APY

**Expected Time**: 2-3 minutes

---

## 📱 Mobile Usage Tips

### Best Practices:
1. **Use portrait mode** for better scrolling
2. **Tap Quick Picks** for instant results
3. **Pinch to zoom** on charts
4. **Swipe between tabs** at top
5. **Use sidebar sparingly** (expands over content)

### Mobile-Optimized Features:
- Larger touch targets (48px minimum)
- Stacked layouts (no side-by-side on small screens)
- Simplified animations (better performance)
- Larger fonts (easier reading)

---

## 🎨 Understanding Visual Elements

### Color Meanings

| Color | Meaning | Example |
|-------|---------|---------|
| 🟢 Green | Good/Positive | High APY, low complaints |
| 🔴 Red | Bad/Negative | Low APY, high APR |
| 🟣 Purple | Interactive/CTA | Buttons, links |
| 🟠 Orange | Warning/Benchmark | Fed rate line, alerts |
| ⚪ Gray | Neutral/Info | Labels, secondary text |

### Icons & Badges

| Icon | Meaning |
|------|---------|
| 🥇🥈🥉 | Rankings (1st, 2nd, 3rd) |
| 🏆 | Top performer / winner |
| ⚡ | Hot / trending up |
| 💎 | Premium / excellent quality |
| 🛡️ | Safe / secure |
| ⭐ | Recommended |
| ⚠️ | Warning / caution |
| ✅ | Success / completed |

---

## 🔧 Advanced Features

### Sidebar Filters

**Multi-Bank Selection**:
- Click dropdown → Search for banks
- Select multiple banks
- Results update automatically
- See comparison across all selected

**Product Category**:
- Filter by: All / Checking & Savings / Credit Cards / Loans
- Complaint data updates to show only relevant issues

**Time Range**:
- 3 months: Recent trends
- 6 months: Short-term patterns
- 12 months: Annual view
- 3 years: Long-term trends

**Credit Unions**:
- Toggle on to include 10 major credit unions
- Compare CU rates vs. bank rates
- See membership requirements

### Data Refresh

**When to refresh**:
- First time using the app (loads cached data)
- When you want latest government data (bypasses cache)
- After major rate changes announced

**How to refresh**:
1. Click **"↻ Refresh Live Data"** button in sidebar
2. Wait 5-15 seconds for fresh data from APIs
3. All charts and metrics update automatically

---

## 💡 Pro Tips

### Tip 1: Compare Apples to Apples
- Don't just look at APY in isolation
- Check complaint scores and safety ratings
- A bank with 4.50% APY and F safety grade < 4.25% APY with A safety

### Tip 2: Use the Calculator for Every Decision
- Abstract percentages are hard to grasp
- See real dollar amounts: $473/year is more concrete than "4.74% difference"

### Tip 3: Check Multiple Tabs
- Overview: Quick snapshot
- Rate Intel: Verify actual numbers
- Complaints: Check customer experience
- Safety: Ensure bank is sound

### Tip 4: Look for Patterns
- If a bank has high rates but many complaints → investigate why
- If a bank has low rates but great service → might be worth it for branch access

### Tip 5: Mobile vs Desktop
- **Mobile**: Quick picks, calculator, quiz
- **Desktop**: Deep dives, detailed charts, multi-bank comparison

---

## ❓ FAQ

### Q: How often is data updated?
**A**: 
- FDIC/CFPB data: Daily
- Rate data: Updated quarterly (or manually)
- Cached for 1 hour after first fetch
- Click Refresh to force new data

### Q: Are these banks paying for placement?
**A**: No. All data comes from government APIs. No affiliate links or sponsored rankings.

### Q: What if my bank isn't listed?
**A**: Currently tracking 19 major banks + 10 credit unions. More coming in future updates.

### Q: Can I save my comparisons?
**A**: Not yet, but it's on the roadmap. For now, use browser bookmarks.

### Q: Is my data tracked?
**A**: No analytics, no tracking. Your selections stay in your browser session only.

### Q: How accurate are the rates?
**A**: Rates are from published sources (FDIC, FRED, bank websites). Always verify with the bank before opening an account.

### Q: What's the difference between banks and credit unions?
**A**:
- **Banks**: For-profit, open to anyone, FDIC insured
- **Credit Unions**: Non-profit, membership required, NCUA insured
- **CUs typically**: Higher savings rates, lower loan rates, better service
- **Banks typically**: More branches, better mobile apps, more products

---

## 🚨 Troubleshooting

### Problem: Charts not loading
**Solution**: 
1. Check internet connection
2. Click Refresh button
3. Try different browser
4. Check browser console for errors

### Problem: Data seems outdated
**Solution**: Click "↻ Refresh Live Data" in sidebar

### Problem: Calculator shows $0 difference
**Solution**: Make sure you selected different banks in the dropdowns

### Problem: Quiz results seem generic
**Solution**: Results are templated but based on your inputs. Try different answer combinations.

### Problem: Mobile layout looks broken
**Solution**: 
1. Try landscape mode
2. Update to latest Streamlit version
3. Clear browser cache
4. Use Chrome/Safari (best support)

---

## 📞 Support & Feedback

### Found a bug?
Open an issue on GitHub with:
- Screenshot of the problem
- Browser and device info
- Steps to reproduce

### Have a suggestion?
- Feature requests welcome
- Especially interested in:
  - New banks/CUs to add
  - Additional data sources
  - UI/UX improvements

### Want to contribute?
- Fork the repo
- Make your changes
- Submit a pull request
- See CONTRIBUTING.md for guidelines

---

## 🎓 Learning Resources

### Understanding Banking Terms

**APY (Annual Percentage Yield)**: What you earn on savings
- 4.75% APY = $475 earned per $10,000 per year
- Higher is better for savers

**APR (Annual Percentage Rate)**: What you pay on loans/cards
- 24.99% APR = $2,499 interest on $10,000 balance per year
- Lower is better for borrowers

**Tier 1 Capital Ratio**: Bank's safety cushion
- >10% = Well-capitalized (safe)
- 8-10% = Adequate
- <8% = Undercapitalized (risky)

**CFPB Relief Rate**: % complaints resolved with money back
- >30% = Bank actually helps customers
- 10-30% = Some resolution
- <10% = Bank dismisses most complaints

**Fed Funds Rate**: Federal Reserve's benchmark
- Currently ~5.33%
- Banks should pass most of this to savers
- If savings APY < 1%, bank is keeping 4.33%+

---

**Happy banking! 🏦✨**
