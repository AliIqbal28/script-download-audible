# import pathlib
#
# import audible
# import httpx
#
#
# # get download link(s) for book
# def _get_download_link(auth, asin, codec="LC_64_22050_stereo"):
#     # need at least v0.4.0dev
#     if auth.adp_token is None:
#         raise Exception("No adp token present. Can't get download link.")
#
#     try:
#         content_url = ("https://cde-ta-g7g.amazon.com/FionaCDEServiceEngine/"
#                        "FSDownloadContent")
#         params = {
#             'type': 'AUDI',
#             'currentTransportMethod': 'WIFI',
#             'key': asin,
#             'codec': codec
#         }
#         r = httpx.get(
#             url=content_url,
#             params=params,
#             # allow_redirects=False,
#             auth=auth
#         )
#
#         # prepare link
#         # see https://github.com/mkb79/Audible/issues/3#issuecomment-518099852
#         link = r.headers['Location']
#         tld = auth.locale.domain
#         new_link = link.replace("cds.audible.com", f"cds.audible.{tld}")
#         return new_link
#     except Exception as e:
#         print(f"Error: {e}")
#         return
#
#
# def download_file(url):
#     r = httpx.get(url)
#
#     try:
#         title = r.headers["Content-Disposition"].split("filename=")[1]
#         filename = pathlib.Path.cwd() / "audiobooks" / title
#
#         with open(filename, 'wb') as f:
#             for chunk in r.iter_bytes():
#                 f.write(chunk)
#         print(f"File downloaded in {r.elapsed}")
#         return filename
#     except KeyError:
#         return "Nothing downloaded"
#
#
# if __name__ == "__main__":
#     auth = audible.Authenticator.from_file("cred.txt")
#     client = audible.Client(auth)
#
#     books = client.get(
#         path="library",
#         params={
#             "response_groups": "product_attrs",
#             "num_results": "999"
#         }
#     )
#
#     asins = [book["asin"] for book in books["items"]]
#
#     for asin in asins:
#         dl_link = _get_download_link(auth, asin)
#
#         if dl_link:
#             print(f"download link now: {dl_link}")
#             status = download_file(dl_link)
#             print(f"downloaded file: {status}")




import json
import pathlib

import audible
import httpx
from audible.aescipher import decrypt_voucher_from_licenserequest


# files downloaded via this script can be converted
# audible uses a new format (aaxc instead of aax)
# more informations and workaround here:
# https://github.com/mkb79/Audible/issues/3
# especially: https://github.com/mkb79/Audible/issues/3#issuecomment-705262614


# get license response for book
def get_license_response(client, asin, quality):
    try:
        response = client.post(
            f"content/{asin}/licenserequest",
            body={
                "drm_type": "Adrm",
                "consumption_type": "Download",
                "quality": quality
            }
        )
        return response
    except Exception as e:
        print(f"Error: {e}")
        return


def get_download_link(license_response):
    return license_response["content_license"]["content_metadata"]["content_url"]["offline_url"]


def download_file(url, filename):
    headers = {
        "User-Agent": "Audible/671 CFNetwork/1240.0.4 Darwin/20.6.0"
    }
    with httpx.stream("GET", url, headers=headers) as r:
        with open(filename, 'wb') as f:
            for chunck in r.iter_bytes():
                f.write(chunck)
    return filename


if __name__ == "__main__":
    auth = audible.Authenticator.from_file("cred.txt")
    client = audible.Client(auth)

    books = client.get(
        path="library",
        params={
            "response_groups": "product_attrs",
            "num_results": "999"
            }
    )

    for book in books["items"]:
        asin = book["asin"]
        title = f"( {asin}).aaxc"
        lr = get_license_response(client, asin, quality="Extreme")

        if lr:
            # download book
            dl_link = get_download_link(lr)
            filename = pathlib.Path.cwd() / "audiobooks" / title
            print(f"download link now: {dl_link}")
            status = download_file(dl_link, filename)
            print(f"downloaded file: {status} to {filename}")

            # save voucher
            voucher_file = filename.with_suffix(".json")
            decrypted_voucher = decrypt_voucher_from_licenserequest(auth, lr)
            voucher_file.write_text(json.dumps(decrypted_voucher, indent=4))
            print(f"saved voucher to: {voucher_file}")