# Adani Group Rewards & Recognition

A Django-based employee rewards and recognition system where employees can send peer reward tokens within a monthly allowance.

## Features

- Employee login with email and password.
- Monthly token allowance per employee.
- Peer-to-peer recognition with category, message, and token amount.
- Validation to prevent self-rewards and over-sending tokens.
- Recognition feed, token wallet, and leaderboard.
- Staff-only admin panel showing all employees.
- Django admin screens for profiles and recognitions.
- Reward catalog where employees can redeem received points.
- Demo data command for quick testing.

## Setup

```powershell
.\\.venv\\Scripts\\activate
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Open `http://127.0.0.1:8000/` and login with:

- Email: `nayan@adani.example`
- Password: `password123`

The demo `nayan` user is staff-enabled. Visit `http://127.0.0.1:8000/admin-panel/` for the employee admin panel or `http://127.0.0.1:8000/admin/` for Django admin.

Demo roles:

- `nayan@adani.example`: Admin, can access both admin panels and participate in rewards.
- `aisha@adani.example`: Staff, can access the employee admin panel and participate in rewards.
- `rahul@adani.example`: Staff, can access the employee admin panel and participate in rewards.
- `priya@adani.example` and `kabir@adani.example`: Employees, can send and receive rewards.
