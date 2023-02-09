# Yes4All Test Case Solution

Table of contents

* [Yes4All Test Case Solution](#Yes4All-Test-Case-Solution)
   * [Vấn đề](#vấn-đề)
   * [Cài đặt](#cài-đặt)
   * [Demo](#demo)
      * [Database](#database)
   * [Phương pháp, quá trình thực hiện](#phương-pháp-quá-trình-thực-hiện)
   * [Khó khăn và giải pháp](#khó-khăn-và-giải-pháp)

****

# Vấn đề

  

Trước khi bắt đầu, mình đọc qua các yêu cầu để biết vấn đề của bài toán này là gì. Xây dựng data pipeline thu thập dữ liệu từ trang web, trong đó có các yêu cầu đặt ra như sau:

- Lấy danh sách category cấp thấp hơn

- Lấy danh sách best seller nằm trong category

- Lấy thông tin chi tiết của từng sản phẩm

  

Dựa trên các yêu cầu như trên, mình sẽ xây dựng một database diagram như sau:

  

![as](https://i.imgur.com/acDbKbB.png)

  

Điều này có thay đổi một chút về những thông tin cần lấy tại bảng `best_seller` so với yêu cầu gốc khi không chứa thông tin giá và tên sản phẩm, thay vào đó ta có thể truy vấn các thông tin này khi join hai bảng `best_seller` và `asin_info` lại với nhau. Việc này sẽ làm giảm redundant data như tên, giá ở bảng `best_seller`, ngoài ra về mặt bản chất có một số sản phẩm giá hiển thị ở trang best seller của category hiển thị không phải là giá của sản phẩm đó nếu sản phẩm đó unavailable. 

Do đó để giảm sự phức tạp về logic lấy giá sản phẩm cũng như tránh conflict về giá cả nếu xuất hiện ở cả hai bảng thì ở bảng `best_seller` mình sẽ không lấy giá và tên sản phẩm.


![join-best_seller-and-asin_info](https://i.imgur.com/tdAEk35.png)

## Cài đặt

Đầu tiên clone repository này về máy

```
git clone git@github.com:vuthanhdatt/yes4all-test-case.git

cd yes4all-test-case/
```

Sau đó tạo một virtual environment và cài đặt các thư viện cần thiết vào môi trường ảo này, tránh xung đột với các thư viện sẵn có.

```
# tạo môi trường ảo tên .yes4all
python3 -m venv .yes4all

# Activate 

source .yes4all/bin/activate

# Cài đặt các thư viện cần thiết

pip install -r requirements.txt
```

## Demo
Mình có tạo một file tên `demo.py` để demo kết quả các yêu cầu đặt ra. File demo này hoạt động như một cli, sau khi cài đặt xong các thư viện cần thiết, chạy câu lệnh sau `python3 demo.py -h` để xem cách sử dụng:

```
python3 demo.py -h

usage: demo.py [-h] [-gcc GET_CHILD_CATEGORY] [-bsi BEST_SELLER_ITEMS] [-dai DETAIL_ASIN_INFO [DETAIL_ASIN_INFO ...]]

Demo Yes4All Test Case

optional arguments:
  -h, --help            show this help message and exit
  -gcc GET_CHILD_CATEGORY, --get-child-category GET_CHILD_CATEGORY
                        Get children categories information of given parent category
  -bsi BEST_SELLER_ITEMS, --best-seller-items BEST_SELLER_ITEMS
                        Get 100 best seller items of given category
  -dai DETAIL_ASIN_INFO [DETAIL_ASIN_INFO ...], --detail-asin-info DETAIL_ASIN_INFO [DETAIL_ASIN_INFO ...]
                        Get detail information of given asin item
```

Cụ thể thì mình tạo 3 arguments tương ứng với 3 yêu cầu đặt ra. 
- Để lấy tất cả danh sách category cấp thấp hơn category được cho. Chạy câu lệnh `python3 demo.py -gcc category_id`:

![](https://i.imgur.com/EM7g921.png)

Ở hình trên, mình lấy categories cấp thấp hơn của category có id `16225007011`, đây là category Computer mà trong đề bài yêu cầu. Ta có thể thấy Computer có 11 categories cấp thấp hơn.

- Để lấy danh sách sản phẩm best_seller nằm trong category, chạy câu lệnh `python3 demo.py -bsi category_id`:

```
❯_: python3 demo.py -bsi 193870011
       cat_id rank     asin_id                              asin_url
0   193870011    1  B07CRG94G3  https://www.amazon.com/dp/B07CRG94G3
1   193870011    2  B07MJW5BXZ  https://www.amazon.com/dp/B07MJW5BXZ
2   193870011    3  B0795DP124  https://www.amazon.com/dp/B0795DP124
3   193870011    4  B08HN37XC1  https://www.amazon.com/dp/B08HN37XC1
4   193870011    5  B07MFZXR1B  https://www.amazon.com/dp/B07MFZXR1B
..        ...  ...         ...                                   ...
95  193870011   96  B0BDTC589G  https://www.amazon.com/dp/B0BDTC589G
96  193870011   97  B08Y1Q2KSZ  https://www.amazon.com/dp/B08Y1Q2KSZ
97  193870011   98  B011K4XZQ0  https://www.amazon.com/dp/B011K4XZQ0
98  193870011   99  B08RX4QKXS  https://www.amazon.com/dp/B08RX4QKXS
99  193870011  100  B07ZGJVTZK  https://www.amazon.com/dp/B07ZGJVTZK

[100 rows x 4 columns]

```
Ở đây mình lấy danh sách best_seller của category `193870011`, tức là category Computer Components. Có thể thay đổi category id với các id khác lấy được từ câu lệnh lấy categories cấp thấp hơn ở trên như `172456` tương ứng với Computer Accessories & Peripherals, `3011391011` tương ứng với Laptop Accessories. Lưu ý là danh sách best seller thường xuyên thay đổi nên kết quả khi chạy có thể khác với kết quả ở trên.


- Để lấy thông tin chi tiết của sản phẩm, chạy câu lệnh `python3 demo.py -dai asin_id`

```
❯_: python3 demo.py -dai B07CRG94G3 
https://www.amazon.com/dp/B07CRG94G3 normal
Get data from 1 asin took 3.3957 seconds
      asin_id  ...                                            img_url
0  B07CRG94G3  ...  https://m.media-amazon.com/images/I/81tjLksKix...

[1 rows x 7 columns]

```

Ở đây mình lấy thông tin của sản phẩm có asin_id là `B07CRG94G3`. Có thể lấy nhiều sản phẩm cùng lúc bằng cách thêm nhiều asin_id khác phía sau. Các asin_id có thể lấy từ câu lệnh lấy danh sách best seller ở trên như `B07MJW5BXZ` , `B0795DP124` etc...

### Database

Đề bài yêu cầu xây dựng một data pipeline nên mình có tạo file `ingest_data.py` để đưa các thông tin crawl được vào database. Mình sử dụng Docker để chạy PostgreSQL database và PgAdmin để quản lý. Ngoaì ra mình cũng lưu data crawl được vào folder `data` ở local.

- Để set up PostgreSQL cùng Docker, đầu tiên cần tạo thư mục để mount data, giúp cho data không bị mất mỗi lần dừng docker container.

```
mkdir -p db/pgadmin
sudo chown 5050:5050 db/pgadmin/
```

- Sau đó chạy `docker compose up -d` để bắt đầu. Dùng lệnh `docker ps` để xem danh sách các container đang chạy.

```
❯_: docker ps
CONTAINER ID   IMAGE            COMMAND                  CREATED       STATUS             PORTS                                            NAMES
1d321a95019a   postgres:13      "docker-entrypoint.s…"   9 hours ago   Up About an hour   0.0.0.0:5432->5432/tcp, :::5432->5432/tcp        pgdatabase_container
b55907642e38   dpage/pgadmin4   "/entrypoint.sh"         9 hours ago   Up About an hour   443/tcp, 0.0.0.0:8080->80/tcp, :::8080->80/tcp   pgadmin_container
```

Nếu kết quả xuất hiện có 2 container đang chạy, một cái sử dụng postgres image, một cái sử dụng pgadmin4 image thì đã set up thành công. Lúc này có thể chạy file `ingest_data.py` để đưa data crawl được vào PostgreSQL. Để tiết kiệm thời gian thì mình chỉ lấy 300 sản phẩm best seller của 3 categories với mục đích demo.

- Để truy cập vào giao diện quản lý PgAdmin, mở địa chỉ `localhost:8080/browser/` trong browser. Đăng nhập với thông tin email: `admin@admin.com`, password: `root`. Sau khi đăng nhập thành công, kết nối với PostgreSQL với thông tin

```
hostname: pgdatabase
username: postgres
password: root
```

![](https://i.imgur.com/E1naCDm.png)

Sau khi chạy xong file `ingest_data.py` thành công, ta sẽ thấy có 3 table đã đưuọc thêm vào PostgreSQL trong giao diện quản lý pgadmin.

![](https://i.imgur.com/jaUnvla.png)


## Phương pháp, quá trình thực hiện

Mình dùng synchronous request với package [requests](https://requests.readthedocs.io/en/latest/) để get các thông tin cần ít số lần requests như lấy thông tin categories con và danh sách best_seller. Đối với thông tin chi tiết của từng item, do phải requests tới nhiều item nên mình dùng asynchronous requests, với [aiohttp](https://docs.aiohttp.org/en/stable/) và [asyncio](https://docs.python.org/3/library/asyncio.html). Để kiểm soát số lượng request tới amazon, tránh việc block IP hay captcha, mình dùng [Token Bucket algorithm](https://dev.to/satrobit/rate-limiting-using-the-token-bucket-algorithm-3cjh). 

Lợi ích lớn nhất của asynchronous requests theo mình thấy chính là việc kiểm soát được tốc độ lấy dữ liệu cũng như tận dụng thời gian hiệu quả hơn so với synchronous request.

Sau khi request tới các địa chỉ cần crawl từ Amazon, mình dùng [bs4](https://www.crummy.com/software/BeautifulSoup/bs4/doc/) để extract các thông tin cần thiết.

Để đưa các thông tin crawl được vào database, mình biến đổi dữ liệu raw crawl được với [pandas](https://pandas.pydata.org/) về đúng format mong muốn, sau đó dùng [SQLAlchemy](https://docs.sqlalchemy.org/en/20/) để connect tới database và đưa dữ liệu đã được xử lý vào. Trong quá trình làm thì có một [bug](https://github.com/pandas-dev/pandas/issues/51015) với pandas và SQLAlchemy version 2 trở lên nên mình phải downgrade SQLAlchemy về version 1.4.46 mới fix được.

## Khó khăn và giải pháp

- Giá sản phẩm: Khó khăn đầu tiên chính là lấy giá các sản phẩm do có nhiều UI cho trang sản phẩm, dẫn tới mỗi UI lại có các tag gắn với giá sản phẩm khác nhau. Mình không thể cover tất cả các trường hợp có thể xảy ra nhưng về cơ bản, logic lấy giá sản phẩm của mình như sau. Đầu tiên chia sản phẩm ra 3 dạng - availabe, not availabe in Vietnam, và unavailabe. Sau đó cover các trường hợp có thể xảy ra đối với từng dạng sản phẩm này. Đối với sản phẩm unavailabe mình sẽ để giá là N/A, vì không hiển thị giá trên trang sản phẩm chi tiết. Có một lưu ý ở đây là tuy ở trang sản phẩm chi tiết là unavailabe và không có giá cụ thể, ở trang best seller vẫn có giá của một số sản phẩm dạng này. Đây là giá offer availabe, có thể là giá của sản phẩm này nhưng là hàng cũ chẳng hạn. Do hạn chế về mặt thời gian nên mình nghĩ logic lấy giá của mình vẫn có bỏ sót nhiều edge case và không hoàn toàn chính xác 100%, tuy nhiên với logic mình đã implement, mình nghĩ đây là một logic không quá phức tạp và vẫn có thể cover hầu hết các trường hợp xảy ra.

- Captcha: Amazon kiểm soát việc crawl data khá gắt gao, mình đã bị ban IP dù đã thận trọng crawl với tốc độ thấp. Hiện tại thì mình chỉ mới hạn chế việc dính captcha bằng cách giảm tốc độ request và rotate User-Agent, tuy nhiên tốc độ khoảng 200-300s cho 100 items là khá chậm, mình cũng chưa test với tốc độ lớn hơn để tìm ra tốc độ tối ưu . Tuy nhiên có một giải pháp tối ưu hơn để giải quyết vấn đề captcha là sử dụng package [amazoncaptcha](https://pypi.org/project/amazoncaptcha/) để solve captcha. Package này được cập nhật gần đây nên có vẻ sẽ hoạt động tốt. Trong tương lai nếu cần lấy thông tin của hàng trăm ngàn sản phẩm thì vấn đề cải thiện tốc độ cần được ưu tiên đầu tiên. Ngoài việc solve captcha thì còn có thể sử dựng proxy để rotate IP address từ đó tăng tốc độ crawl dữ liệu.

- Exception/Logging: Khi cần lấy dữ liệu của một lượng lớn sản phẩm - hàng trăm ngàn, chắc chắn sẽ xảy ra những error không mong muốn, do đó để tracking quá trình crawl hiệu quả hơn, cần implement việc logging cũng như catching exception hiệu quả hơn. Hiện tại mình chỉ mới implement một cách cơ bản cũng như in ra terminal chứ chưa logging.

- Database Optimization: Hiện tại thì mình chỉ mới biến đổi kiểu dữ liệu trước khi đưa vào database, khi truy vấn hay join bảng với hàng trăm ngàn row cần set index cũng như thiết lập constraint giữa các bảng để việc truy vấn dữ liệu tối ưu hơn.



