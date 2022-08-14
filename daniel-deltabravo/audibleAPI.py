import audible
import pathlib
import httpx


def custom_captcha_callback(captcha_url):
    print(captcha_url)
    guess = input("Answer for CAPTCHA: ")
    guess = str(guess).strip().lower()
    return guess


# This is supposed to run only once
# Authorize and register in one step
auth = audible.Authenticator.from_login(
    "", #amazon username
    "",#amazon password
    locale="us",
    with_username=False,
    captcha_callback=custom_captcha_callback,
)

# Save credendtials to file
auth.to_file("cred.txt")
auth = audible.Authenticator.from_file("cred.txt")
client = audible.Client(auth=auth)
library = client.get(
    'library',
    num_results=1000,
    response_groups=','.join([
        'series',
        'product_desc',
        'product_attrs',
    ]),
    sort_by='Author',
)

license = client.post(
   "content/B07KKMNZCH/licenserequest",
    body={
        "drm_type": "Adrm",
        "consumption_type": "Download",
        "quality":"Extreme"
    }
)
# content_url = license['content_license']['content_metadata']['content_url']['offline_url']

print(license)
