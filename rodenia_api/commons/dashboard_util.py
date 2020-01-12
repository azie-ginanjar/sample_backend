from datetime import datetime, timedelta
from rodenia_api.models import ShopeeOrderItem
from rodenia_api.extensions import db
from sqlalchemy import cast, Date, String
from sqlalchemy.sql import text
from collections import Counter
from decimal import Decimal
from rodenia_api.commons import util


class AllPlatformStats:
    def __init__(self, shopee_stats, lazada_stats):
        """
        args:
        lazada_stats = instance of LazadaStats() class
        shopee_stats = instance of ShopeeStats() class
        """
        self.lazada_stats = lazada_stats
        self.shopee_stats = shopee_stats

    def get_net_profit(self):
        return self.lazada_stats.get_net_profit() + self.shopee_stats.get_net_profit()

    def get_gross_profit(self):
        return self.lazada_stats.get_gross_profit() + self.shopee_stats.get_gross_profit()

    def get_total_cost(self):
        return self.lazada_stats.get_total_cost() + self.shopee_stats.get_total_cost()

    def get_chart_data(self):
        """
        the assumption here is that the result from both get_chart_data() from Lazada and Shopee class
        will always have the same set of keys and length of dict since we are using the same timestamps and applying the 
        same intervals. The only thing that might be different is how we compute for profit and revenue but
        that's already abstracted on each class, so when combining both chart data, we only care about adding
        profit and revenue for same dates on each dictionaries.
        """
        combined_chart_data = {}
        shopee_chart_data = self.shopee_stats.get_chart_data()
        lazada_chart_data = self.lazada_stats.get_chart_data()
        print("stat", self.shopee_stats)

        for key, val in shopee_chart_data.items():
            shopee = Counter(shopee_chart_data[key])
            # uncomment when we have code for lazada
            # lazada = Counter(lazada_chart_data[key])
            # shopee.update(lazada)
            combined_chart_data[key] = dict(shopee)

        return combined_chart_data

    def get_all_stats(self):
        return {
            "net_profit": util.safe_float(self.get_net_profit()),
            "gross_profit": util.safe_float(self.get_gross_profit()),
            "total_cost": util.safe_float(self.get_total_cost()),
            "chart_data": self.get_chart_data()
        }


class LazadaStats:
    def __init__(self, min_timestamp, max_timestamp, seller_id):
        self.min_timestamp = min_timestamp
        self.max_timestamp = max_timestamp
        self.seller_id = seller_id

    def get_net_profit(self):
        return 0

    def get_gross_profit(self):
        return 0

    def get_total_cost(self):
        return 0

    def get_chart_data(self):
        return {}

    def get_all_stats(self):
        return {
            "net_profit": util.safe_float(self.get_net_profit()),
            "gross_profit": util.safe_float(self.get_gross_profit()),
            "total_cost": util.safe_float(self.get_total_cost()),
            "chart_data": self.get_chart_data()
        }


class ShopeeStats:
    def __init__(self, min_timestamp, max_timestamp, shop_id):
        self.min_timestamp = min_timestamp
        self.max_timestamp = max_timestamp
        self.shop_id = shop_id

    def get_net_profit(self):
        """
        escrow_amount
        The total amount that the seller is expected to receive for the order.
        This amount includes buyer paid order amount (total_amount), all forms of Shopee platform subsidy; a
        nd offset by any cost and commission incurred.
        """
        sql = """
            SELECT COALESCE(SUM(escrow_amount), 0.00)
            FROM shopee_order 
            WHERE  to_timestamp(create_time)::date BETWEEN :start_date AND :end_date
            AND shop_id = :shop_id
        """

        net_profit = db.engine.execute(text(sql), {
            "start_date": self.min_timestamp, "end_date": self.max_timestamp, "shop_id": self.shop_id}).scalar()

        print("im net profit", net_profit - Decimal(str(self.get_total_cost())))
        return net_profit - Decimal(str(self.get_total_cost()))

    def get_gross_profit(self):
        """
        total_amount
        The total amount paid by the buyer for the order.
        This amount includes the total sale price of items, shipping cost beared by buyer; 
        and offset by Shopee promotions if applicable. 
        This value will only return after the buyer has completed payment for the order.
        """
        sql = """
            SELECT COALESCE(SUM(total_amount), 0.00)
            FROM shopee_order
            WHERE  to_timestamp(create_time)::date BETWEEN :start_date AND :end_date
            AND shop_id = :shop_id
         """

        gross_profit = db.engine.execute(text(sql), {
            "start_date": self.min_timestamp, "end_date": self.max_timestamp, "shop_id": self.shop_id}).scalar()

        print("gross profit", gross_profit)
        return gross_profit - Decimal(str(self.get_total_cost()))

    def get_total_cost(self):
        sql = """
            SELECT COALESCE(SUM(cost), 0.00)
            FROM (
                SELECT COALESCE(shopee_order_item.variation_quantity_purchased * shopee_inventory_item.buy_cost, 0.00) AS cost
                FROM shopee_order_item
                LEFT JOIN shopee_inventory_item ON shopee_order_item.item_id = shopee_inventory_item.item_id
                JOIN shopee_order ON shopee_order_item.order_id = shopee_order.order_id
                WHERE to_timestamp(shopee_order.create_time)::date BETWEEN :start_date AND :end_date
                AND shopee_order_item.shop_id = :shop_id
            ) q1;
         """

        total_cost = db.engine.execute(text(sql), {
            "start_date": self.min_timestamp, "end_date": self.max_timestamp, "shop_id": self.shop_id}).scalar()

        return total_cost

    def parse_chart_query_result(self, chart_data):
        result = {}
        for row in chart_data:
            result[row.interval.date().isoformat()] = {
                "profit": util.safe_float(row.profit),
                "revenue": util.safe_float(row.revenue)
            }

        return result

    def get_chart_data(self):
        min_timestamp = datetime.strptime(self.min_timestamp, "%Y-%m-%d").date()
        max_timestamp = datetime.strptime(self.max_timestamp, "%Y-%m-%d").date()
        date_difference_in_days = abs((max_timestamp - min_timestamp).days)

        if date_difference_in_days <= 14:
            interval = '1 day'
            date_part = 'day'
        # skipping 3 day interval for now as date_trunc doesn't really support it.
        elif 14 <= date_difference_in_days <= 90:
            interval = '1 week'
            date_part = 'week'
        elif date_difference_in_days > 90:
            interval = '1 month'
            date_part = 'month'

        sql = """
        SELECT day as "interval", CAST(COALESCE(profit, 0.00) AS TEXT) as profit, CAST(COALESCE(revenue, 0.00) AS TEXT) AS revenue
            FROM  (
            SELECT  day::date
            FROM   generate_series(date_trunc(:date_part,timestamp :start_date)
                                    , timestamp :end_date
                                    , interval  :interval) day
            ) d
            LEFT JOIN (
            SELECT date_trunc(:date_part, to_timestamp(create_time)::date) AS day
                    , SUM(escrow_amount) AS profit, sum(total_amount) as revenue
            FROM   (
            select order_id, escrow_amount, total_amount, create_time from shopee_order
            WHERE  to_timestamp(create_time)::date BETWEEN :start_date AND :end_date
            AND shop_id = :shop_id

            ) t2 GROUP  BY 1
            ) t USING (day)
        ORDER  BY day
        """

        chart_data = db.engine.execute(text(sql), {
            "date_part":  date_part,
            "interval": interval,
            "start_date": self.min_timestamp,
            "end_date": self.max_timestamp,
            "shop_id": self.shop_id
        })

        chart_data = self.parse_chart_query_result(chart_data)

        return chart_data

    def get_all_stats(self):
        return {
            "net_profit": util.safe_float(self.get_net_profit()),
            "gross_profit": util.safe_float(self.get_gross_profit()),
            "total_cost": util.safe_float(self.get_total_cost()),
            "chart_data": util.safe_float(self.get_chart_data())
        }
