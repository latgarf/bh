CREATE TABLE "opened" (
    "time_ordered" varchar(14) NOT NULL,
    "product_id" varchar(4) NOT NULL,
    "time_expiry" varchar(14) NOT NULL,
    "amount_ordered" decimal NOT NULL,
    "addr_user" varchar(32) NOT NULL,
    "addr_our" varchar(32) NOT NULL,
    "fee_quoted" decimal NOT NULL,
    "rate" decimal NOT NULL,
    "status" integer NOT NULL,
    "order_id" varchar(32) NOT NULL PRIMARY KEY,
    "query_id" varchar(32) NOT NULL,
    "time_opened" varchar(14),
    "payment_received" decimal,
    "amount_opened" decimal,
    "time_closed" varchar(14),
    "time_paid" varchar(14),
    "payment_sent" decimal
);

INSERT INTO opened SELECT time_ordered, product_id, time_expiry, amount_ordered, addr_user, addr_our, fee_quoted, rate, status, order_id, query_id, null, null, null,null, null, null FROM submitted;

CREATE TABLE "transaction_ids" (
    "order_id" varchar(32) NOT NULL PRIMARY KEY,
    "transaction_id" varchar(64) NOT NULL
);

CREATE TABLE "bitstamp_history" (
    "trade_id" INTEGER PRIMARY KEY,
    "ts" varchar(14) NOT NULL,
    "tid" varchar(10) NOT NULL,
    "price" decimal NOT NULL,
    "amount" decimal NOT NULL
);
