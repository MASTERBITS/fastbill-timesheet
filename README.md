# fastbill-timesheet

fastbill-timesheet is a Python script to create monthly pdf timesheets based on your fastbill time tracking.

## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install requirements (requests, reportlab).

```bash
pip install -r requirements.txt
```

## Usage

```
export API_USER=[fastbill email] API_KEY=[api-key]

python fastbill_timesheet.py [internal_project_id] [year-month]
```
## Example

```
export API_USER=your@email.com API_KEY=yourapikeynotyourpasswordcheckfastbillsettings

# last month
python fastbill_timesheet.py 123456

# specific month
python fastbill_timesheet.py 123456 2022-02
```

## How to get the fastbill internal project id?
Use the [fastbill api](https://apidocs.fastbill.com/fastbill/de/project.html#project.get) or go into the fastbill webfrontend, open your browser inspector and select your project. 


## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

## Credits
[Erwan Martin / ZeWaren](https://zewaren.net/reportlab.html) - How to write a table into a PDF using Python and Reportlab

## License
[MIT](https://choosealicense.com/licenses/mit/)