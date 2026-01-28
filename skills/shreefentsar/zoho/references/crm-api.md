# Zoho CRM API Reference

## Modules
- Leads, Contacts, Accounts, Deals, Tasks, Events, Calls, Notes, Products, Quotes, Sales_Orders, Purchase_Orders, Invoices

## Common Fields (Deals)
- Deal_Name, Amount, Stage, Closing_Date, Account_Name, Contact_Name, Pipeline, Probability, Description

## Common Fields (Contacts)
- First_Name, Last_Name, Email, Phone, Mobile, Account_Name, Title, Department

## Common Fields (Leads)
- First_Name, Last_Name, Email, Company, Phone, Lead_Source, Lead_Status, Industry

## Search Criteria Operators
- equals, not_equal, starts_with, contains, not_contains, in, not_in, between, greater_than, less_than

## Pagination
- `page` and `per_page` params (max 200 per page)
- Response includes `info.more_records` boolean

## Sorting
- `sort_by` and `sort_order` (asc/desc)
