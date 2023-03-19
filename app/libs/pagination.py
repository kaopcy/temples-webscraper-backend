import math
from fastapi import HTTPException, status


class Pagination:
    collections = []
    amount = 5
    current_page = 0

    collection_on_page = []

    def __init__(self, collection=[]):
        self.collections = collection

    def set_amount_per_page(self, amount):
        self.amount = amount
        return self

    def set_current_page(self, current_page):
        self.current_page = current_page

        if current_page > self.get_available_page():
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, detail="invalid current page")

        start_index = (self.current_page - 1) * self.amount
        end_index = self.get_available_page() if self.current_page * \
            self.amount > self.get_available_page() else self.current_page * self.amount

        self.collection_on_page = self.collections[start_index:end_index]
        return self.collection_on_page

    def get_available_page(self):
        return math.ceil(len(self.collections) / self.amount)

    def get_collections(self, current_page):
        if current_page:
            self.set_current_page(current_page)

        return self.collection_on_page
