import json
from datetime import datetime
from typing import Any, Dict, List

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from src.models.schemas.user import UserCreate
from src.securities.authorization.jwt import create_access_token


@pytest.mark.asyncio
async def test_create_expense(client, create_test_category, user_token):
    category_id = create_test_category["category_id"]

    expense_data = {
        "category_id": category_id,
        "subject": "Business Lunch",
        "expense_date": "2024-09-18",
        "amount": 50,
        "reimbursable": False,
        "description": "Lunch with a client",
        "employee": "John Doe",
    }

    files = {"invoice_image": ("", b"", "application/octet-stream")}
    data = {"expense": json.dumps(expense_data)}

    multipart_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "multipart/form-data; boundary=------WebKitFormBoundaryF6sSRjfPR0gJB7xK",
    }

    response = await client.post("/expenses", headers=multipart_headers, data=data, files=files)

    assert (
        response.status_code == status.HTTP_201_CREATED
    ), f"Expected 201, but got {response.status_code}. Content: {response.content.decode()}"
    response_data = response.json()

    assert response_data["subject"] == "Business Lunch"
    assert response_data["amount"] == 50
    assert response_data["reimbursable"] is False
    assert response_data["description"] == "Lunch with a client"
    assert response_data["employee"] == "John Doe"


@pytest.mark.asyncio
async def test_fetch_all_expenses(client: AsyncClient, db: AsyncSession, create_test_category, user_token):
    category_id = create_test_category["category_id"]
    expense_data = {
        "category_id": category_id,
        "subject": "Business Lunch",
        "expense_date": "2024-09-18",
        "amount": 50,
        "reimbursable": False,
        "description": "Lunch with a client",
        "employee": "John Doe",
    }

    files = {"invoice_image": ("", b"", "application/octet-stream")}
    data = {"expense": json.dumps(expense_data)}

    multipart_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "multipart/form-data; boundary=------WebKitFormBoundaryF6sSRjfPR0gJB7xK",
    }

    response = await client.post("/expenses", headers=multipart_headers, data=data, files=files)
    assert response.status_code == status.HTTP_201_CREATED

    fetch_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_token}",
    }

    response = await client.get("/expenses/all", headers=fetch_headers)

    assert response.status_code == status.HTTP_200_OK, f"Expected 200, got {response.status_code}"
    expenses = response.json()

    assert len(expenses) == 1, "There should be one expense"
    assert expenses[0]["subject"] == "Business Lunch"
    assert expenses[0]["amount"] == 50
    assert expenses[0]["reimbursable"] is False
    assert expenses[0]["description"] == "Lunch with a client"
    assert expenses[0]["employee"] == "John Doe"


@pytest.mark.asyncio
async def test_fetch_all_expenses_no_data(client: AsyncClient, user_token):
    fetch_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_token}",
    }

    response = await client.get("/expenses/all", headers=fetch_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND, f"Expected 404, got {response.status_code}"


@pytest.mark.asyncio
async def test_get_recent_expenses(client: AsyncClient, db: AsyncSession, create_test_category, user_token):
    category_id = create_test_category["category_id"]

    expense_data_list = [
        {"subject": "Expense 5", "amount": 104.0, "expense_date": "2024-09-15"},
        {"subject": "Expense 4", "amount": 103.0, "expense_date": "2024-09-16"},
        {"subject": "Expense 3", "amount": 102.0, "expense_date": "2024-09-17"},
        {"subject": "Expense 2", "amount": 101.0, "expense_date": "2024-09-18"},
        {"subject": "Expense 1", "amount": 100.0, "expense_date": "2024-09-19"},
    ]

    for expense_data in expense_data_list:
        expense = {
            "category_id": category_id,
            "subject": expense_data["subject"],
            "expense_date": expense_data["expense_date"],
            "amount": expense_data["amount"],
            "reimbursable": False,
            "description": f"Description for {expense_data['subject']}",
            "employee": "John Doe",
        }

        files = {"invoice_image": ("", b"", "application/octet-stream")}
        data = {"expense": json.dumps(expense)}
        multipart_headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "multipart/form-data; boundary=------WebKitFormBoundaryF6sSRjfPR0gJB7xK",
        }

        await client.post("/expenses", headers=multipart_headers, data=data, files=files)

    fetch_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_token}",
    }

    response = await client.get("/expenses/recent", headers=fetch_headers)

    assert response.status_code == status.HTTP_200_OK, f"Expected 200, got {response.status_code}"
    recent_expenses = response.json()

    assert len(recent_expenses) == 5, "Expected 5 recent expenses"


@pytest.mark.asyncio
async def test_get_recent_expenses_no_data(client: AsyncClient, user_token):
    fetch_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_token}",
    }

    response = await client.get("/expenses/recent", headers=fetch_headers)

    assert response.status_code == status.HTTP_404_NOT_FOUND, f"Expected 404, got {response.status_code}"


import json
from typing import Any, Dict, List

import pytest
from fastapi import status
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession


@pytest.mark.asyncio
async def test_list_expenses(
    client: AsyncClient, db: AsyncSession, create_test_category: Dict[str, Any], user_token: str
):
    category_id = create_test_category["category_id"]
    expense_data_list = [
        {"subject": "Expense 1", "amount": 100.0, "expense_date": "2024-09-01", "employee": "John Doe"},
        {"subject": "Expense 2", "amount": 200.0, "expense_date": "2024-09-02", "employee": "Jane Doe"},
        {"subject": "Expense 3", "amount": 150.0, "expense_date": "2024-09-03", "employee": "John Doe"},
        {"subject": "Expense 4", "amount": 120.0, "expense_date": "2024-09-04", "employee": "John Doe"},
        {"subject": "Expense 5", "amount": 130.0, "expense_date": "2024-09-05", "employee": "Jane Doe"},
    ]

    for expense_data in expense_data_list:
        expense = {
            "category_id": category_id,
            "subject": expense_data["subject"],
            "expense_date": expense_data["expense_date"],
            "amount": expense_data["amount"],
            "reimbursable": False,
            "description": f"Description for {expense_data['subject']}",
            "employee": expense_data["employee"],
        }

        files = {"invoice_image": ("", b"", "application/octet-stream")}
        data = {"expense": json.dumps(expense)}
        multipart_headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "multipart/form-data; boundary=------WebKitFormBoundaryF6sSRjfPR0gJB7xK",
        }

        response = await client.post("/expenses", headers=multipart_headers, data=data, files=files)
        assert response.status_code == status.HTTP_201_CREATED, f"Failed to create expense: {response.text}"

    # Test sorting
    response = await client.get(
        "/expenses", headers={"Authorization": f"Bearer {user_token}"}, params={"sort_order": "desc"}
    )
    assert response.status_code == status.HTTP_200_OK, f"Expected 200, got {response.status_code}"
    res_data: Dict[str, Any] = response.json()

    assert "items" in res_data
    assert isinstance(res_data["items"], list)
    assert len(res_data["items"]) == 5
    assert res_data["items"][0]["subject"] == "Expense 5"
    assert res_data["items"][-1]["subject"] == "Expense 1"

    # Test filtering
    response = await client.get(
        "/expenses", headers={"Authorization": f"Bearer {user_token}"}, params={"search": "Expense 2"}
    )
    assert response.status_code == status.HTTP_200_OK, f"Expected 200, got {response.status_code}"
    filtered_data: Dict[str, Any] = response.json()

    assert "items" in filtered_data
    assert isinstance(filtered_data["items"], list)
    assert len(filtered_data["items"]) == 1
    assert filtered_data["items"][0]["subject"] == "Expense 2"

    # Test pagination
    response = await client.get(
        "/expenses", headers={"Authorization": f"Bearer {user_token}"}, params={"page": 1, "size": 2}
    )
    assert response.status_code == status.HTTP_200_OK, f"Expected 200, got {response.status_code}"
    paginated_data: Dict[str, Any] = response.json()

    assert "items" in paginated_data
    assert isinstance(paginated_data["items"], list)
    assert len(paginated_data["items"]) == 2
    assert paginated_data["items"][0]["subject"] == "Expense 5"
    assert paginated_data["items"][1]["subject"] == "Expense 4"


@pytest.mark.asyncio
async def test_get_available_years(client: AsyncClient, db: AsyncSession, create_test_category, user_token):
    category_id = create_test_category["category_id"]
    years = [2021, 2022, 2023]
    subjects = ["Expense 1", "Expense 2", "Expense 3"]

    for year in years:
        for i, subject in enumerate(subjects):
            expense_data = {
                "category_id": category_id,
                "subject": subject,
                "expense_date": f"{year}-01-01",
                "amount": 100 + i,
                "reimbursable": False,
                "description": f"Description for {subject}",
                "employee": "John Doe",
            }

            files = {"invoice_image": ("", b"", "application/octet-stream")}
            data = {"expense": json.dumps(expense_data)}
            multipart_headers = {
                "accept": "application/json",
                "Authorization": f"Bearer {user_token}",
                "Content-Type": "multipart/form-data; boundary=------WebKitFormBoundaryF6sSRjfPR0gJB7xK",
            }

            await client.post("/expenses", headers=multipart_headers, data=data, files=files)

    response = await client.get("/expenses/available-years", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == status.HTTP_200_OK, f"Expected 200, got {response.status_code}"
    available_years = response.json()

    assert available_years == sorted(
        years, reverse=True
    ), f"Expected {sorted(years, reverse=True)}, but got {available_years}"


@pytest.mark.asyncio
async def test_get_expenses_by_category_recent_year(
    client: AsyncClient, db: AsyncSession, create_test_category, user_token
):
    category_id = create_test_category["category_id"]
    current_year = 2023
    amounts = [10, 20, 30, 40, 50]
    for i, amount in enumerate(amounts):
        expense_data = {
            "category_id": category_id,
            "subject": f"Expense {i + 1}",
            "expense_date": f"{current_year}-01-01",
            "amount": amount,
            "reimbursable": False,
            "description": f"Description for Expense {i + 1}",
            "employee": "John Doe",
        }
        files = {"invoice_image": ("", b"", "application/octet-stream")}
        data = {"expense": json.dumps(expense_data)}
        multipart_headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "multipart/form-data; boundary=------WebKitFormBoundaryF6sSRjfPR0gJB7xK",
        }
        response = await client.post("/expenses", headers=multipart_headers, data=data, files=files)
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), f"Failed to create expense. Status: {response.status_code}, Response: {response.text}"

    response = await client.get("/expenses/by-category", headers={"Authorization": f"Bearer {user_token}"})
    assert response.status_code == status.HTTP_200_OK, f"Expected 200, got {response.status_code}"
    expenses_by_category = response.json()

    assert len(expenses_by_category) == 1
    assert expenses_by_category[0]["category"] == create_test_category["name"]
    total_amount = sum(amounts)
    assert expenses_by_category[0]["amount"] == total_amount


@pytest.mark.asyncio
async def test_get_last_5_months_summary(client: AsyncClient, db: AsyncSession, create_test_category, user_token):
    category_id = create_test_category["category_id"]
    year = 2024
    months = ["Jul", "Aug", "Sep", "Oct", "Nov", "Dec"]

    amounts = [100, 200, 150, 300, 250, 50]
    start_month = 7

    for i, amount in enumerate(amounts):
        expense_data = {
            "category_id": category_id,
            "subject": f"Expense {i + 1}",
            "expense_date": f"{year}-{start_month + i:02d}-01",
            "amount": amount,
            "reimbursable": False,
            "description": f"Description for Expense {i + 1}",
            "employee": "John Doe",
        }

        files = {"invoice_image": ("", b"", "application/octet-stream")}
        data = {"expense": json.dumps(expense_data)}
        multipart_headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "multipart/form-data; boundary=------WebKitFormBoundaryF6sSRjfPR0gJB7xK",
        }
        response = await client.post("/expenses", headers=multipart_headers, data=data, files=files)

        assert (
            response.status_code == status.HTTP_201_CREATED
        ), f"Failed to create expense. Status: {response.status_code}, Response: {response.text}"

    response = await client.get(
        f"/expenses/last_5_months?year={year}", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK, f"Expected 200, got {response.status_code}"

    last_5_months_summary = response.json()

    expected_months = months[1:6]
    expected_amounts = amounts[1:6]

    assert len(last_5_months_summary) == 5

    for month, expected_amount in zip(expected_months, expected_amounts):
        assert any(
            record["month"] == month and record["amount"] == expected_amount for record in last_5_months_summary
        )


@pytest.mark.asyncio
async def test_get_general_summary(client: AsyncClient, db: AsyncSession, create_test_category, user_token):
    category_id = create_test_category["category_id"]
    year = datetime.now().year

    expenses = [
        {"category_id": category_id, "subject": "Expense 1", "expense_date": f"{year}-01-15", "amount": 100},
        {"category_id": category_id, "subject": "Expense 2", "expense_date": f"{year}-02-20", "amount": 200},
        {"category_id": category_id, "subject": "Expense 3", "expense_date": f"{year}-03-25", "amount": 150},
        {"category_id": category_id, "subject": "Expense 4", "expense_date": f"{year}-04-10", "amount": 300},
        {"category_id": category_id, "subject": "Expense 5", "expense_date": f"{year}-07-05", "amount": 250},
        {"category_id": category_id, "subject": "Expense 6", "expense_date": f"{year}-08-15", "amount": 50},
    ]

    for expense in expenses:
        files = {"invoice_image": ("", b"", "application/octet-stream")}
        data = {"expense": json.dumps(expense)}
        multipart_headers = {
            "accept": "application/json",
            "Authorization": f"Bearer {user_token}",
            "Content-Type": "multipart/form-data; boundary=------WebKitFormBoundaryF6sSRjfPR0gJB7xK",
        }
        response = await client.post("/expenses", headers=multipart_headers, data=data, files=files)
        assert (
            response.status_code == status.HTTP_201_CREATED
        ), f"Failed to create expense. Status: {response.status_code}, Response: {response.text}"

    response = await client.get(
        f"/expenses/general-summary?year={year}", headers={"Authorization": f"Bearer {user_token}"}
    )
    assert response.status_code == status.HTTP_200_OK, f"Expected 200, got {response.status_code}"

    general_summary = response.json()

    expected_total_spending = 1050.00
    expected_this_month = 0.00
    expected_last_month = 50.00
    expected_this_quarter = 300.00
    expected_last_quarter = 300.00

    assert (
        general_summary["total_spending"] == expected_total_spending
    ), f"Expected total spending: {expected_total_spending}, got {general_summary['total_spending']}"
    assert (
        general_summary["this_month"] == expected_this_month
    ), f"Expected this month spending: {expected_this_month}, got {general_summary['this_month']}"
    assert (
        general_summary["last_month"] == expected_last_month
    ), f"Expected last month spending: {expected_last_month}, got {general_summary['last_month']}"
    assert (
        general_summary["this_quarter"] == expected_this_quarter
    ), f"Expected this quarter spending: {expected_this_quarter}, got {general_summary['this_quarter']}"
    assert (
        general_summary["last_quarter"] == expected_last_quarter
    ), f"Expected last quarter spending: {expected_last_quarter}, got {general_summary['last_quarter']}"


@pytest.mark.asyncio
async def test_get_expense_endpoint(client: AsyncClient, db: AsyncSession, create_test_category, user_token):
    category_id = create_test_category["category_id"]

    expense_data = {
        "category_id": category_id,
        "subject": "Business Lunch",
        "expense_date": "2024-09-18",
        "amount": 50,
        "reimbursable": False,
        "description": "Lunch with a client",
        "employee": "John Doe",
    }

    files = {"invoice_image": ("", b"", "application/octet-stream")}
    data = {"expense": json.dumps(expense_data)}

    multipart_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "multipart/form-data; boundary=------WebKitFormBoundaryF6sSRjfPR0gJB7xK",
    }

    response = await client.post("/expenses", headers=multipart_headers, data=data, files=files)

    response_expense_data = response.json()
    expense_id = response_expense_data["expenses_id"]

    response = await client.get(f"/expenses/{expense_id}", headers={"Authorization": f"Bearer {user_token}"})

    assert response.status_code == status.HTTP_200_OK, f"Expected 200, got {response.status_code}"

    expense = response.json()

    assert expense["expenses_id"] == str(expense_id), f"Expected expense ID {expense_id}, got {expense['expenses_id']}"
    assert expense["category_id"] == category_id, f"Expected category ID {category_id}, got {expense['category_id']}"
    assert (
        expense["subject"] == expense_data["subject"]
    ), f"Expected subject {expense_data['subject']}, got {expense['subject']}"
    assert (
        expense["expense_date"] == expense_data["expense_date"]
    ), f"Expected expense_date {expense_data['expense_date']}, got {expense['expense_date']}"
    assert (
        expense["amount"] == expense_data["amount"]
    ), f"Expected amount {expense_data['amount']}, got {expense['amount']}"
    assert (
        expense["reimbursable"] == expense_data["reimbursable"]
    ), f"Expected reimbursable {expense_data['reimbursable']}, got {expense['reimbursable']}"
    assert (
        expense["description"] == expense_data["description"]
    ), f"Expected description {expense_data['description']}, got {expense['description']}"
    assert (
        expense["employee"] == expense_data["employee"]
    ), f"Expected employee {expense_data['employee']}, got {expense['employee']}"


@pytest.mark.asyncio
async def test_update_expense_endpoint(client: AsyncClient, db: AsyncSession, create_test_category, user_token):
    category_id = create_test_category["category_id"]

    initial_expense_data = {
        "category_id": category_id,
        "subject": "Business Lunch",
        "expense_date": "2024-09-18",
        "amount": 50,
        "reimbursable": False,
        "description": "Lunch with a client",
        "employee": "John Doe",
    }

    files = {"invoice_image": ("", b"", "application/octet-stream")}
    data = {"expense": json.dumps(initial_expense_data)}
    multipart_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "multipart/form-data; boundary=------WebKitFormBoundaryF6sSRjfPR0gJB7xK",
    }

    response = await client.post("/expenses", headers=multipart_headers, data=data, files=files)

    response_expense_data = response.json()
    expense_id = response_expense_data["expenses_id"]
    updated_expense_data = {
        "category_id": category_id,
        "subject": "Updated Business Lunch",
        "expense_date": "2024-09-20",
        "amount": 75,
        "reimbursable": True,
        "description": "Updated description",
        "employee": "Jane Doe",
    }

    update_data = {"expense_update": json.dumps(updated_expense_data)}

    update_response = await client.put(
        f"/expenses/{expense_id}", headers=multipart_headers, data=update_data, files=files
    )

    assert update_response.status_code == status.HTTP_200_OK, f"Expected 200, got {update_response.status_code}"

    updated_expense = update_response.json()

    assert updated_expense["expenses_id"] == str(
        expense_id
    ), f"Expected expense ID {expense_id}, got {updated_expense['expenses_id']}"
    assert (
        updated_expense["category_id"] == category_id
    ), f"Expected category ID {category_id}, got {updated_expense['category_id']}"
    assert (
        updated_expense["subject"] == updated_expense_data["subject"]
    ), f"Expected subject {updated_expense_data['subject']}, got {updated_expense['subject']}"
    assert (
        updated_expense["expense_date"] == updated_expense_data["expense_date"]
    ), f"Expected expense_date {updated_expense_data['expense_date']}, got {updated_expense['expense_date']}"
    assert (
        updated_expense["amount"] == updated_expense_data["amount"]
    ), f"Expected amount {updated_expense_data['amount']}, got {updated_expense['amount']}"
    assert (
        updated_expense["reimbursable"] == updated_expense_data["reimbursable"]
    ), f"Expected reimbursable {updated_expense_data['reimbursable']}, got {updated_expense['reimbursable']}"
    assert (
        updated_expense["description"] == updated_expense_data["description"]
    ), f"Expected description {updated_expense_data['description']}, got {updated_expense['description']}"
    assert (
        updated_expense["employee"] == updated_expense_data["employee"]
    ), f"Expected employee {updated_expense_data['employee']}, got {updated_expense['employee']}"


@pytest.mark.asyncio
async def test_delete_expense_endpoint(client: AsyncClient, db: AsyncSession, create_test_category, user_token):

    category_id = create_test_category["category_id"]

    expense_data = {
        "category_id": category_id,
        "subject": "Team Outing",
        "expense_date": "2024-09-18",
        "amount": 120,
        "reimbursable": True,
        "description": "Lunch for team outing",
        "employee": "Jane Doe",
    }

    files = {"invoice_image": ("", b"", "application/octet-stream")}
    data = {"expense": json.dumps(expense_data)}

    multipart_headers = {
        "accept": "application/json",
        "Authorization": f"Bearer {user_token}",
        "Content-Type": "multipart/form-data; boundary=------WebKitFormBoundaryF6sSRjfPR0gJB7xK",
    }

    response = await client.post("/expenses", headers=multipart_headers, data=data, files=files)

    response_expense_data = response.json()
    expense_id = response_expense_data["expenses_id"]

    response = await client.delete(f"/expenses/{expense_id}", headers={"Authorization": f"Bearer {user_token}"})

    assert response.status_code == status.HTTP_200_OK, f"Expected 200, got {response.status_code}"
    delete_response = response.json()
    assert (
        delete_response["message"] == "Expense deleted successfully"
    ), f"Expected success message, got {delete_response['message']}"

    response = await client.get(f"/expenses/{expense_id}", headers={"Authorization": f"Bearer {user_token}"})

    assert response.status_code == status.HTTP_404_NOT_FOUND, f"Expected 404, got {response.status_code}"
