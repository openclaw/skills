---
name: kenya-tax-rates
description: Calculate Kenya payroll deductions - PAYE, SHIF, NSSF, Housing Levy with accurate 2024/2025 rates
---

# Kenya Tax Rates Skill

Calculate Kenya payroll taxes and deductions with up-to-date rates for PAYE, SHIF, NSSF, and Housing Levy.

## Features

- **PAYE** - 5-band progressive tax (10% to 35%)
- **SHIF** - 2.75% Social Health Insurance (replaced NHIF Oct 2024)
- **NSSF** - Two-tier pension with auto date-based limits
- **Housing Levy** - 1.5% Affordable Housing Levy
- **Tax Reliefs** - Personal, insurance, pension, mortgage

## Usage

Install the npm package:

```bash
npm install kenya-tax-rates
```

### Quick Net Salary

```typescript
import { getNetSalary } from 'kenya-tax-rates';

const netSalary = getNetSalary(100000);
// Returns ~KES 75,000
```

### Full Payroll Breakdown

```typescript
import { calculatePayroll } from 'kenya-tax-rates';

const result = calculatePayroll({
  grossSalary: 100000,
  pensionContribution: 5000,  // optional
  insurancePremium: 2000,     // optional
});

// Returns:
// {
//   grossSalary: 100000,
//   taxableIncome: 93590,
//   deductions: { shif: 2750, nssf: 2160, housingLevy: 1500, paye: 18594 },
//   netSalary: 74995,
//   employerContributions: { nssf: 2160, housingLevy: 1500 }
// }
```

### Individual Calculators

```typescript
import { calculatePaye, calculateShif, calculateNssf, calculateHousingLevy } from 'kenya-tax-rates';

// PAYE with reliefs
const paye = calculatePaye(85000);

// SHIF (2.75%, min KES 300, no cap)
const shif = calculateShif(50000); // 1375

// NSSF (auto-detects 2024/2025 rates based on current date)
const nssf = calculateNssf(80000);

// Housing Levy (1.5%)
const levy = calculateHousingLevy(100000); // 1500
```

## Current Tax Rates

### PAYE Monthly Bands
| Income (KES) | Rate |
|--------------|------|
| 0 - 24,000 | 10% |
| 24,001 - 32,333 | 25% |
| 32,334 - 500,000 | 30% |
| 500,001 - 800,000 | 32.5% |
| Above 800,000 | 35% |

### NSSF Limits (auto-selected by date)
| Period | Lower Limit | Upper Limit | Max Contribution |
|--------|-------------|-------------|------------------|
| Feb 2024 - Jan 2025 | KES 7,000 | KES 36,000 | KES 2,160 |
| From Feb 2025 | KES 8,000 | KES 72,000 | KES 4,320 |

### Reliefs
- Personal Relief: KES 2,400/month
- Insurance Relief: 15% of premiums, max KES 5,000/month
- Pension Deduction: Max KES 30,000/month

## API Reference

| Function | Description |
|----------|-------------|
| `calculatePayroll(input)` | Full payroll with all deductions |
| `getNetSalary(gross, date?)` | Quick net salary calculation |
| `calculatePaye(taxableIncome)` | PAYE with reliefs |
| `calculateShif(grossSalary)` | SHIF contribution |
| `calculateNssf(earnings, date?)` | NSSF two-tier contribution |
| `calculateHousingLevy(grossSalary)` | Housing levy (1.5%) |

## Source

- npm: [kenya-tax-rates](https://www.npmjs.com/package/kenya-tax-rates)
- GitHub: [enjuguna/kenya-tax-rates](https://github.com/enjuguna/kenya-tax-rates)
