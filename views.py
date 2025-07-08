import requests
from django.shortcuts import render, redirect, get_object_or_404
from .models import Book, Member, Transaction
from django.utils import timezone
from django.db.models import Q
from django.contrib import messages

def home(request):
    return render(request, 'base.html')

def book_list(request):
    query = request.GET.get('q', '')
    if query:
        books = Book.objects.filter(Q(title__icontains=query) | Q(author__icontains=query))
    else:
        books = Book.objects.all()
    return render(request, 'book_list.html', {'books': books, 'query': query})

def member_list(request):
    members = Member.objects.all()
    return render(request, 'member_list.html', {'members': members})

def transaction_list(request):
    transactions = Transaction.objects.all().order_by('-issue_date')
    return render(request, 'transaction_list.html', {'transactions': transactions})

def issue_book(request, book_id, member_id):
    book = get_object_or_404(Book, id=book_id)
    member = get_object_or_404(Member, id=member_id)

    if book.stock <= 0:
        messages.error(request, "Book out of stock.")
        return redirect('book_list')

    if member.debt >= 500:
        messages.error(request, "Member has debt ≥ ₹500.")
        return redirect('member_list')

    Transaction.objects.create(book=book, member=member)
    book.stock -= 1
    book.save()

    messages.success(request, f"{book.title} issued to {member.name}.")
    return redirect('transaction_list')



def return_book(request, txn_id):
    txn = get_object_or_404(Transaction, id=txn_id)

    if txn.returned:
        messages.warning(request, "Book already returned.")
        return redirect('transaction_list')

    txn.return_date = timezone.now().date()
    txn.returned = True

    issue_date = txn.issue_date
    if hasattr(issue_date, 'date'):
        issue_date = issue_date.date()

    days_borrowed = (txn.return_date - issue_date).days
    extra_days = max(0, days_borrowed - 7)
    fee = extra_days * 10

    txn.rent_fee = fee
    txn.save()

    # Increase stock
    book = txn.book
    book.stock += 1
    book.save()

    # Add fee to member's debt
    member = txn.member
    member.debt += fee
    member.save()

    messages.success(request, f"Book returned. Fee ₹{fee} added to {member.name}.")
    return redirect('transaction_list')

def import_books(request):
    if request.method == 'POST':
        num_books = int(request.POST.get('num_books', 20))
        title = request.POST.get('title', '')

        imported = 0
        page = 1

        while imported < num_books:
            url = f'https://frappe.io/api/method/frappe-library?page={page}&title={title}'
            response = requests.get(url)

            if response.status_code == 200:
                data = response.json().get('message', [])
                if not data:
                    break  # No more data

                for item in data:
                    if imported >= num_books:
                        break

                    Book.objects.get_or_create(
                        title=item.get('title', ''),
                        author=item.get('authors', ''),
                        isbn=item.get('isbn', ''),
                        publisher=item.get('publisher', ''),
                        pages=int(item.get('num_pages') or 0),
                        defaults={'stock': 1}
                    )
                    imported += 1

                page += 1
            else:
                messages.error(request, "Error fetching from Frappe API.")
                break

        messages.success(request, f"{imported} books imported successfully.")
        return redirect('book_list')

    return render(request, 'import_books.html')

def add_member(request):
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        debt = float(request.POST.get("debt", 0))

        # if debt > 500:
        #     messages.error(request, "Debt cannot exceed ₹500 when adding a new member.")
        #     return redirect('member_list')

        member = Member.objects.create(name=name, email=email, debt=debt)
        messages.success(request, f"Member {member.name} added successfully!")
        return redirect('member_list')
