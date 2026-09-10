# MyClinicProtocols fulfillment service

This private service is the secure half of checkout. It is intentionally kept
separate from the public static assets.

Workflow:

1. Store the clinic intake and create a PayPal Order with the internal order
   reference in `custom_id`.
2. Capture and verify the PayPal Order on the server.
3. Generate a clearly marked draft DOCX and PDF for each requested treatment.
4. Store the files privately and issue an expiring, signed download URL.
5. Email the download URL to the buyer and send the order notification to
   `myclinicprotocols@gmail.com`.
6. Record delivery of the RN-reviewed version. Its delivery timestamp starts
   the 14-calendar-day revision window. A maximum of two revision rounds is
   accepted, with a 3–5-business-day turnaround.

The instant output is not the RN-reviewed version and must retain the label
`DRAFT — Qualified Provider Review Required`.

## Local verification

```bash
python -m unittest fulfillment.test_documents
```

Production activation still requires PayPal API credentials, private object
storage, a transactional email provider, and deployment of the API service.
Never commit those credentials or proprietary reviewed source documents.

## Required production secrets

Copy the names in `.env.example` into the hosting provider's encrypted secret
manager. Do not commit real values. Start in `PAYPAL_MODE=sandbox`; switch to
`live` only after a successful full sandbox purchase, download, and email test.

The container stores orders under `/data`, which must be a private persistent
volume. For multi-instance deployment, replace the local SQLite/filesystem
adapter with a managed database and private object storage.
