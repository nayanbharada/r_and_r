# Business Requirements Document

## Project Name

Adani Group Employee Rewards and Recognition System

## Purpose

The purpose of this system is to provide Adani Group employees with a simple digital platform to recognize colleagues through reward tokens. Employees can send tokens to peers for valuable contributions, view recognition activity, and redeem received points for available rewards. Admin and staff users can monitor employee reward activity and manage the recognition ecosystem.

## Business Objectives

- Encourage peer-to-peer recognition across departments.
- Build a transparent rewards culture where employee contributions are visible.
- Limit token distribution through monthly employee allowances.
- Allow employees to redeem received recognition points.
- Give admin and staff users visibility into employees, roles, token usage, and redemption activity.
- Support different user roles while keeping every user eligible to give and receive rewards.

## Stakeholders

- Employees
- Staff users
- Admin users
- HR team
- Department managers
- System administrator

## User Roles

### Employee

Employees can:

- Login using email and password.
- Send reward tokens to other employees.
- Receive reward tokens from other employees.
- View their monthly sending balance.
- View recognition feed and leaderboard.
- Redeem received points for rewards.

### Staff

Staff users can:

- Perform all employee actions.
- Access the employee admin panel.
- View all employees and reward balances.
- Monitor token and redemption activity.

### Admin

Admin users can:

- Perform all employee and staff actions.
- Access the employee admin panel.
- Access Django admin.
- Manage employee profiles, rewards, recognitions, and redemptions.

## Current Demo Users

All demo users use password `password123`.

| Email | Role |
| --- | --- |
| nayan@adani.example | Admin |
| aisha@adani.example | Staff |
| rahul@adani.example | Staff |
| priya@adani.example | Employee |
| kabir@adani.example | Employee |

## Functional Requirements

### Authentication

- The system must allow users to login using email and password.
- The system must redirect unauthenticated users to the login page.
- The system must support role-based access after login.

### Employee Rewards

- Employees must be able to select another employee as the reward receiver.
- Employees must not be able to reward themselves.
- Employees must enter the number of tokens to send.
- Employees must select a recognition category.
- Employees must enter a recognition message.
- The system must deduct sent tokens from the sender’s monthly allowance.
- The system must prevent users from sending more tokens than their available monthly balance.

### Monthly Token Limit

- Each employee must have a monthly token allowance.
- The system must track tokens sent during the current month.
- The system must calculate remaining monthly tokens.
- The system must reset monthly sent-token usage when a new month begins.

### Recognition Feed

- The dashboard must show recent recognition activity.
- Each recognition must show receiver, sender, category, token count, message, and date.
- The dashboard must show total tokens shared and total recognition moments.

### Leaderboard

- The system must show top recognized employees.
- Leaderboard ranking must be based on received tokens.
- The leaderboard must show employee name, department, recognition count, and token total.

### Redemption

- Employees must be able to view available reward items.
- Employees must be able to redeem received points.
- Redeemable points must equal received points minus already redeemed points.
- The system must prevent redemption when the employee has insufficient points.
- The system must prevent redemption when a reward is out of stock.
- The system must reduce reward stock after successful redemption.
- The system must keep redemption history for each employee.

### Admin Panel

- Staff and admin users must access the employee admin panel.
- Employee users must not access the employee admin panel.
- The admin panel must show all employees.
- The admin panel must show employee role, email, department, designation, allowance, sent tokens, remaining tokens, received points, redeemed points, balance, and active status.
- Admin users must access Django admin for backend management.

### Reward Management

- Admin users must be able to manage reward items in Django admin.
- Reward items must include name, description, required points, stock, and active status.
- Admin users must be able to view redemption records.

## Recognition Categories

- Ownership
- Teamwork
- Innovation
- Customer Impact
- Safety

## Business Rules

- A user can be an employee, staff, or admin.
- Staff and admin users are still employees and can send, receive, and redeem rewards.
- Employees cannot reward themselves.
- Employees cannot send more tokens than their monthly available balance.
- Only received points are redeemable.
- Sent tokens do not increase the sender’s redeemable balance.
- Redeemed points reduce available redemption balance.
- Rewards with zero stock cannot be redeemed.
- Inactive rewards cannot be redeemed.
- Only staff and admin users can access the employee admin panel.
- Only admin users can access Django admin.

## Non-Functional Requirements

- The UI must be attractive, responsive, and easy to use.
- The system must use Django authentication.
- The system must use role-based access control.
- The system must validate all important business rules on the backend.
- The system must store all data in a database.
- The system must provide test coverage for core reward, role, login, and redemption rules.

## Pages and Navigation

| Page | URL | Access |
| --- | --- | --- |
| Login | `/login/` | Public |
| Dashboard | `/` | Authenticated users |
| Redeem Points | `/redeem/` | Authenticated users |
| Employee Admin Panel | `/admin-panel/` | Staff and Admin |
| Django Admin | `/admin/` | Admin |

## Data Entities

### Employee Profile

- User
- Employee ID
- Department
- Designation
- Role
- Monthly token allowance
- Tokens sent this month
- Last reset month

### Recognition

- Sender
- Receiver
- Token count
- Category
- Message
- Created date

### Reward Item

- Name
- Description
- Points required
- Stock
- Active status
- Created date

### Redemption

- Employee
- Reward item
- Status
- Created date

## Acceptance Criteria

- Users can login using email and password.
- Employees can send reward tokens to other employees.
- Employees cannot send tokens to themselves.
- Employees cannot exceed their monthly token limit.
- Staff and admin users can access the employee admin panel.
- Staff and admin users can still send and receive rewards.
- Employees can view redeemable points.
- Employees can redeem points for active in-stock rewards.
- Employees cannot redeem more points than they have.
- Reward stock decreases after successful redemption.
- Admin users can manage employees, reward items, recognitions, and redemptions.
- The test suite passes successfully.

## Out of Scope for Current Version

- Email notifications.
- Approval workflow for redemption fulfillment.
- Payroll or HRMS integration.
- Multi-location configuration.
- Advanced analytics dashboards.
- Mobile app version.
- Single sign-on integration.

## Future Enhancements

- Redemption approval and fulfillment workflow.
- Email or SMS notifications.
- Department-wise analytics.
- Monthly automated token reset job.
- Reward item images.
- Export employee reward reports.
- Manager approval for high-value redemptions.
- Integration with company HR systems.

## Test Coverage Summary

The current system includes automated tests for:

- Email login.
- Token sending.
- Monthly token limit validation.
- Self-reward prevention.
- Admin panel access control.
- Staff/admin role behavior.
- Staff users giving and receiving rewards.
- Redemption with sufficient points.
- Redemption failure with insufficient points.
- Redemption failure for out-of-stock rewards.

