// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
// ■  WinForms 07 - 데이터 바인딩 (Data Binding)            ■
// ■  직원 정보 뷰어 만들기                                  ■
// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
//
// 이 파일에서 배우는 것:
//   1) BindingSource          - 데이터와 컨트롤을 연결하는 다리
//   2) DataBinding to TextBox - 텍스트 박스에 데이터 자동 표시
//   3) BindingList<T>         - 변경사항을 자동 감지하는 목록
//   4) INotifyPropertyChanged - 데이터가 바뀌면 자동으로 알려주는 기능
//
// 비유: 데이터 바인딩은 "자동 칠판" 같은 것입니다.
//       선생님(데이터)이 점수를 바꾸면,
//       칠판(화면)에 자동으로 새 점수가 나타납니다.
//       매번 칠판을 직접 지우고 다시 쓸 필요가 없어요!

using System;
using System.Collections.Generic;
using System.ComponentModel;
using System.Drawing;
using System.Runtime.CompilerServices;
using System.Windows.Forms;

internal static class Program
{
    [STAThread]
    private static void Main()
    {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        Application.Run(new EmployeeViewerForm());
    }
}

// ┌──────────────────────────────────────────────────┐
// │  1부: Employee 클래스 - INotifyPropertyChanged   │
// └──────────────────────────────────────────────────┘
// INotifyPropertyChanged는 "변경 알림 시스템"입니다.
// 택배가 도착하면 문자가 오는 것처럼,
// 데이터가 바뀌면 화면에 "바뀌었어요!" 신호를 보냅니다.
//
// 이 인터페이스를 구현하면:
//   1. 속성(Property) 값이 바뀔 때
//   2. PropertyChanged 이벤트가 발생하고
//   3. 바인딩된 컨트롤이 자동으로 새 값을 표시합니다.
public class Employee : INotifyPropertyChanged
{
    private string _name = "";
    private string _department = "";
    private string _position = "";
    private int _salary;
    private DateTime _hireDate;

    public event PropertyChangedEventHandler? PropertyChanged;

    // ── 이름 속성 ──
    // set에서 OnPropertyChanged()를 호출하면,
    // 이 속성에 연결된 TextBox가 자동으로 업데이트됩니다.
    public string Name
    {
        get => _name;
        set { _name = value; OnPropertyChanged(); }
    }

    public string Department
    {
        get => _department;
        set { _department = value; OnPropertyChanged(); }
    }

    public string Position
    {
        get => _position;
        set { _position = value; OnPropertyChanged(); }
    }

    public int Salary
    {
        get => _salary;
        set { _salary = value; OnPropertyChanged(); OnPropertyChanged(nameof(SalaryText)); }
    }

    public DateTime HireDate
    {
        get => _hireDate;
        set { _hireDate = value; OnPropertyChanged(); OnPropertyChanged(nameof(YearsWorked)); }
    }

    // ── 읽기 전용 계산 속성 ──
    // 다른 속성에서 계산된 값도 바인딩할 수 있습니다.
    public string SalaryText => $"{_salary:#,##0}원";
    public int YearsWorked => (int)((DateTime.Now - _hireDate).TotalDays / 365);

    // [CallerMemberName]은 이 메서드를 호출한 속성의 이름을 자동으로 넣어줍니다.
    // Name 속성에서 호출하면 propertyName = "Name"이 됩니다.
    // 매번 문자열을 직접 쓸 필요가 없어서 편리해요!
    private void OnPropertyChanged([CallerMemberName] string? propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }

    public override string ToString() => $"{Name} ({Department})";
}

// ┌──────────────────────────────────────────────────┐
// │  2부: 직원 정보 뷰어 폼                           │
// └──────────────────────────────────────────────────┘
public sealed class EmployeeViewerForm : Form
{
    private readonly BindingSource _bindingSource;
    private readonly BindingList<Employee> _employees;
    private readonly TextBox _nameBox;
    private readonly TextBox _deptBox;
    private readonly TextBox _posBox;
    private readonly TextBox _salaryBox;
    private readonly DateTimePicker _datePicker;
    private readonly Label _salaryLabel;
    private readonly Label _yearsLabel;
    private readonly ListBox _employeeList;
    private readonly Label _countLabel;

    public EmployeeViewerForm()
    {
        Text = "직원 정보 뷰어 - 데이터 바인딩 학습";
        Size = new Size(750, 520);
        StartPosition = FormStartPosition.CenterScreen;

        // ┌──────────────────────────────────────────┐
        // │  BindingList - 자동 감지 목록              │
        // └──────────────────────────────────────────┘
        // BindingList<T>는 일반 List<T>와 비슷하지만,
        // 항목이 추가/삭제되면 자동으로 알려줍니다.
        // 출석부에 학생을 추가하면 자동으로 인원수가 바뀌는 것과 같아요!
        _employees = new BindingList<Employee>
        {
            new Employee
            {
                Name = "김철수", Department = "개발팀",
                Position = "선임 개발자", Salary = 5500000,
                HireDate = new DateTime(2018, 3, 15)
            },
            new Employee
            {
                Name = "이영희", Department = "디자인팀",
                Position = "수석 디자이너", Salary = 5000000,
                HireDate = new DateTime(2019, 7, 1)
            },
            new Employee
            {
                Name = "박민수", Department = "기획팀",
                Position = "팀장", Salary = 6200000,
                HireDate = new DateTime(2016, 1, 10)
            }
        };

        // ┌──────────────────────────────────────────┐
        // │  BindingSource - 데이터와 컨트롤의 다리    │
        // └──────────────────────────────────────────┘
        // BindingSource는 데이터(직원 목록)와 화면(TextBox)을
        // 연결해주는 다리 역할을 합니다.
        // 도서관 사서가 책(데이터)을 찾아서 손님(컨트롤)에게
        // 건네주는 것과 같아요!
        _bindingSource = new BindingSource
        {
            DataSource = _employees
        };

        // 현재 선택된 항목이 바뀔 때 계산 속성 업데이트
        _bindingSource.CurrentChanged += (s, e) => UpdateCalculatedLabels();

        // ── 레이아웃 구성 ──
        var splitContainer = new SplitContainer
        {
            Dock = DockStyle.Fill,
            SplitterDistance = 200,
            FixedPanel = FixedPanel.Panel1
        };

        // ┌──────────────────────────────────────────┐
        // │  왼쪽: 직원 목록 (ListBox + 바인딩)       │
        // └──────────────────────────────────────────┘
        var leftPanel = new Panel { Dock = DockStyle.Fill, Padding = new Padding(10) };

        leftPanel.Controls.Add(new Label
        {
            Text = "직원 목록",
            Dock = DockStyle.Top,
            Height = 25,
            Font = new Font("맑은 고딕", 11, FontStyle.Bold)
        });

        _employeeList = new ListBox
        {
            Dock = DockStyle.Fill,
            Font = new Font("맑은 고딕", 10),
            // DataSource를 BindingSource로 설정하면
            // 목록이 자동으로 채워지고, 선택이 바뀌면
            // 오른쪽 TextBox도 자동으로 바뀝니다!
            DataSource = _bindingSource,
            DisplayMember = "Name"    // 목록에 Name 속성을 표시
        };
        leftPanel.Controls.Add(_employeeList);

        // 추가/삭제 버튼
        var buttonPanel = new FlowLayoutPanel
        {
            Dock = DockStyle.Bottom,
            Height = 40,
            FlowDirection = FlowDirection.LeftToRight
        };

        var addBtn = new Button { Text = "추가", Width = 70 };
        addBtn.Click += OnAddEmployee;
        var delBtn = new Button { Text = "삭제", Width = 70 };
        delBtn.Click += OnDeleteEmployee;
        buttonPanel.Controls.Add(addBtn);
        buttonPanel.Controls.Add(delBtn);
        leftPanel.Controls.Add(buttonPanel);

        _countLabel = new Label
        {
            Text = $"총 {_employees.Count}명",
            Dock = DockStyle.Bottom,
            Height = 25,
            Font = new Font("맑은 고딕", 9),
            TextAlign = ContentAlignment.MiddleCenter
        };
        leftPanel.Controls.Add(_countLabel);

        splitContainer.Panel1.Controls.Add(leftPanel);

        // ┌──────────────────────────────────────────┐
        // │  오른쪽: 상세 정보 (DataBinding)           │
        // └──────────────────────────────────────────┘
        var rightPanel = new TableLayoutPanel
        {
            Dock = DockStyle.Fill,
            ColumnCount = 2,
            RowCount = 8,
            Padding = new Padding(15)
        };
        rightPanel.ColumnStyles.Add(new ColumnStyle(SizeType.Absolute, 100));
        rightPanel.ColumnStyles.Add(new ColumnStyle(SizeType.Percent, 100));

        // ── DataBindings.Add로 TextBox에 바인딩 ──
        // DataBindings.Add("Text", 소스, "속성이름")
        // "Text" = TextBox의 Text 속성에
        // 소스 = BindingSource (데이터 다리)
        // "속성이름" = Employee의 어떤 속성을 연결할지

        int row = 0;

        // 이름
        rightPanel.Controls.Add(MakeLabel("이름:"), 0, row);
        _nameBox = new TextBox { Dock = DockStyle.Fill, Font = new Font("맑은 고딕", 11) };
        _nameBox.DataBindings.Add("Text", _bindingSource, "Name",
            true,                                    // 서식 적용 여부
            DataSourceUpdateMode.OnPropertyChanged); // 글자를 입력할 때마다 즉시 반영
        rightPanel.Controls.Add(_nameBox, 1, row++);

        // 부서
        rightPanel.Controls.Add(MakeLabel("부서:"), 0, row);
        _deptBox = new TextBox { Dock = DockStyle.Fill, Font = new Font("맑은 고딕", 11) };
        _deptBox.DataBindings.Add("Text", _bindingSource, "Department",
            true, DataSourceUpdateMode.OnPropertyChanged);
        rightPanel.Controls.Add(_deptBox, 1, row++);

        // 직급
        rightPanel.Controls.Add(MakeLabel("직급:"), 0, row);
        _posBox = new TextBox { Dock = DockStyle.Fill, Font = new Font("맑은 고딕", 11) };
        _posBox.DataBindings.Add("Text", _bindingSource, "Position",
            true, DataSourceUpdateMode.OnPropertyChanged);
        rightPanel.Controls.Add(_posBox, 1, row++);

        // 급여 (입력)
        rightPanel.Controls.Add(MakeLabel("급여:"), 0, row);
        _salaryBox = new TextBox { Dock = DockStyle.Fill, Font = new Font("맑은 고딕", 11) };
        _salaryBox.DataBindings.Add("Text", _bindingSource, "Salary",
            true, DataSourceUpdateMode.OnPropertyChanged);
        rightPanel.Controls.Add(_salaryBox, 1, row++);

        // 급여 (포맷된 표시) - 읽기 전용 Label에 바인딩
        rightPanel.Controls.Add(MakeLabel("급여 표시:"), 0, row);
        _salaryLabel = new Label
        {
            Dock = DockStyle.Fill,
            Font = new Font("맑은 고딕", 11, FontStyle.Bold),
            ForeColor = Color.DarkGreen,
            TextAlign = ContentAlignment.MiddleLeft
        };
        _salaryLabel.DataBindings.Add("Text", _bindingSource, "SalaryText");
        rightPanel.Controls.Add(_salaryLabel, 1, row++);

        // 입사일
        rightPanel.Controls.Add(MakeLabel("입사일:"), 0, row);
        _datePicker = new DateTimePicker
        {
            Dock = DockStyle.Fill,
            Font = new Font("맑은 고딕", 11),
            Format = DateTimePickerFormat.Short
        };
        _datePicker.DataBindings.Add("Value", _bindingSource, "HireDate",
            true, DataSourceUpdateMode.OnPropertyChanged);
        rightPanel.Controls.Add(_datePicker, 1, row++);

        // 근속 연수
        rightPanel.Controls.Add(MakeLabel("근속 연수:"), 0, row);
        _yearsLabel = new Label
        {
            Dock = DockStyle.Fill,
            Font = new Font("맑은 고딕", 11),
            TextAlign = ContentAlignment.MiddleLeft
        };
        _yearsLabel.DataBindings.Add("Text", _bindingSource, "YearsWorked");
        rightPanel.Controls.Add(_yearsLabel, 1, row++);

        splitContainer.Panel2.Controls.Add(rightPanel);
        Controls.Add(splitContainer);

        // BindingList의 항목 수가 바뀌면 카운트 업데이트
        _employees.ListChanged += (s, e) =>
        {
            _countLabel.Text = $"총 {_employees.Count}명";
        };

        UpdateCalculatedLabels();
    }

    private Label MakeLabel(string text) => new Label
    {
        Text = text,
        AutoSize = true,
        Font = new Font("맑은 고딕", 10, FontStyle.Bold),
        Anchor = AnchorStyles.Left,
        Margin = new Padding(0, 8, 0, 0)
    };

    private void UpdateCalculatedLabels()
    {
        // 계산된 속성(SalaryText, YearsWorked)은
        // 다른 속성이 바뀔 때 수동으로 갱신이 필요할 수 있습니다.
        _bindingSource.ResetCurrentItem();
    }

    // ┌──────────────────────────────────────────┐
    // │  직원 추가                                │
    // └──────────────────────────────────────────┘
    private void OnAddEmployee(object? sender, EventArgs e)
    {
        // BindingList에 추가하면 ListBox에 자동으로 나타납니다!
        // 직접 ListBox.Items.Add()를 할 필요가 없어요.
        // 이것이 데이터 바인딩의 장점입니다.
        _employees.Add(new Employee
        {
            Name = "신규 직원",
            Department = "미배정",
            Position = "사원",
            Salary = 3000000,
            HireDate = DateTime.Now
        });
        _bindingSource.MoveLast(); // 새로 추가한 항목으로 이동
    }

    // ┌──────────────────────────────────────────┐
    // │  직원 삭제                                │
    // └──────────────────────────────────────────┘
    private void OnDeleteEmployee(object? sender, EventArgs e)
    {
        if (_bindingSource.Current is Employee emp)
        {
            var result = MessageBox.Show(
                $"'{emp.Name}'을(를) 삭제하시겠습니까?",
                "삭제 확인", MessageBoxButtons.YesNo, MessageBoxIcon.Question);
            if (result == DialogResult.Yes)
                _bindingSource.RemoveCurrent();
        }
    }
}
