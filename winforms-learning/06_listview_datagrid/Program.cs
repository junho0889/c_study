// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
// ■  WinForms 06 - ListView와 DataGridView                ■
// ■  연락처 관리 프로그램 만들기                             ■
// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
//
// 이 파일에서 배우는 것:
//   1) ListView     - 탐색기처럼 목록을 보여주는 컨트롤 (도서관 카탈로그)
//   2) Details View - 열(column)이 있는 표 형태 보기
//   3) DataGridView - 엑셀처럼 칸(셀)을 편집할 수 있는 표 (성적표)
//   4) 열(Column) 추가, 행(Row) 추가, 셀 서식, 정렬

using System;
using System.Collections.Generic;
using System.Drawing;
using System.Windows.Forms;

internal static class Program
{
    [STAThread]
    private static void Main()
    {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        Application.Run(new ContactManagerForm());
    }
}

// ┌──────────────────────────────────────────────────┐
// │  연락처 관리자 - ListView + DataGridView 실습     │
// └──────────────────────────────────────────────────┘
public sealed class ContactManagerForm : Form
{
    private readonly ListView _listView;
    private readonly DataGridView _dataGrid;
    private readonly TextBox _nameBox;
    private readonly TextBox _phoneBox;
    private readonly TextBox _emailBox;
    private readonly ComboBox _groupCombo;
    private readonly ToolStripStatusLabel _statusLabel;

    public ContactManagerForm()
    {
        Text = "연락처 관리 - ListView & DataGridView 학습";
        Size = new Size(900, 650);
        StartPosition = FormStartPosition.CenterScreen;

        // ┌──────────────────────────────────────────┐
        // │  탭 컨트롤 - 두 가지 뷰를 탭으로 나누기    │
        // └──────────────────────────────────────────┘
        // TabControl은 공책의 탭(색인표)과 같습니다.
        // "국어" 탭, "수학" 탭처럼 내용을 분류해서 보여줍니다.
        var tabControl = new TabControl
        {
            Dock = DockStyle.Fill,
            Font = new Font("맑은 고딕", 10)
        };

        var listViewTab = new TabPage("ListView 보기");
        var dataGridTab = new TabPage("DataGridView 보기");

        // ┌──────────────────────────────────────────┐
        // │  1부: ListView - 탐색기 스타일 목록        │
        // └──────────────────────────────────────────┘
        // ListView는 Windows 탐색기의 파일 목록과 같습니다.
        // View.Details로 설정하면 열(Column)이 있는 표처럼 보입니다.
        // 도서관의 도서 카탈로그처럼 정리된 목록을 보여줘요!

        _listView = new ListView
        {
            Dock = DockStyle.Fill,
            View = View.Details,         // 열이 있는 상세 보기
            FullRowSelect = true,        // 한 줄 전체 선택 (칸 하나만 X)
            GridLines = true,            // 격자선 표시
            Font = new Font("맑은 고딕", 10)
        };

        // ── 열(Column) 추가 ──
        // 열은 표의 제목줄입니다. "이름", "전화번호" 같은 분류 항목이에요.
        _listView.Columns.Add("이름", 120);     // 너비 120픽셀
        _listView.Columns.Add("전화번호", 130);
        _listView.Columns.Add("이메일", 200);
        _listView.Columns.Add("그룹", 80);

        // ── 열 클릭으로 정렬 ──
        // 도서관에서 "제목순", "저자순"으로 정렬하는 것처럼,
        // 열 제목을 클릭하면 그 열 기준으로 정렬합니다.
        _listView.ColumnClick += (s, e) =>
        {
            _listView.ListViewItemSorter = new ListViewItemComparer(e.Column);
            _listView.Sort();
            _statusLabel.Text = $"{_listView.Columns[e.Column].Text} 기준으로 정렬됨";
        };

        listViewTab.Controls.Add(_listView);

        // ┌──────────────────────────────────────────┐
        // │  2부: DataGridView - 엑셀 스타일 표       │
        // └──────────────────────────────────────────┘
        // DataGridView는 엑셀 스프레드시트와 비슷합니다.
        // 각 칸(셀)을 직접 클릭해서 수정할 수 있어요!
        // 학교 성적표를 만드는 것과 같습니다.

        _dataGrid = new DataGridView
        {
            Dock = DockStyle.Fill,
            Font = new Font("맑은 고딕", 10),
            AllowUserToAddRows = false,          // 사용자가 직접 행 추가 못하게
            SelectionMode = DataGridViewSelectionMode.FullRowSelect,
            AutoSizeColumnsMode = DataGridViewAutoSizeColumnsMode.Fill,
            BackgroundColor = Color.White,
            RowHeadersVisible = false            // 왼쪽 행 번호 숨김
        };

        // ── 열(Column) 정의 ──
        // DataGridView의 열은 종류가 다양합니다:
        //   TextBoxColumn  - 일반 텍스트 입력 (이름, 전화번호)
        //   ComboBoxColumn - 드롭다운 선택 (그룹)
        //   CheckBoxColumn - 체크박스 (즐겨찾기)
        //   ButtonColumn   - 버튼 (삭제)

        _dataGrid.Columns.Add(new DataGridViewTextBoxColumn
        {
            Name = "이름",
            HeaderText = "이름",
            Width = 100
        });

        _dataGrid.Columns.Add(new DataGridViewTextBoxColumn
        {
            Name = "전화번호",
            HeaderText = "전화번호",
            Width = 120
        });

        _dataGrid.Columns.Add(new DataGridViewTextBoxColumn
        {
            Name = "이메일",
            HeaderText = "이메일",
            Width = 180
        });

        var groupColumn = new DataGridViewComboBoxColumn
        {
            Name = "그룹",
            HeaderText = "그룹",
            Width = 80
        };
        groupColumn.Items.AddRange("가족", "친구", "회사", "기타");
        _dataGrid.Columns.Add(groupColumn);

        var favoriteColumn = new DataGridViewCheckBoxColumn
        {
            Name = "즐겨찾기",
            HeaderText = "즐겨찾기",
            Width = 60
        };
        _dataGrid.Columns.Add(favoriteColumn);

        // ── 셀 서식 (Cell Formatting) ──
        // 셀의 모양을 조건에 따라 바꿀 수 있습니다.
        // 시험에서 100점이면 빨간 펜으로 동그라미 치는 것처럼!
        _dataGrid.CellFormatting += (s, e) =>
        {
            // "즐겨찾기" 열이고 값이 true이면 행 전체를 노란색으로
            if (e.ColumnIndex == _dataGrid.Columns["즐겨찾기"]!.Index)
            {
                if (e.Value is true)
                {
                    _dataGrid.Rows[e.RowIndex].DefaultCellStyle.BackColor = Color.LightYellow;
                }
                else
                {
                    _dataGrid.Rows[e.RowIndex].DefaultCellStyle.BackColor = Color.White;
                }
            }
        };

        // ── 열 머리글 스타일 ──
        _dataGrid.EnableHeadersVisualStyles = false;
        _dataGrid.ColumnHeadersDefaultCellStyle = new DataGridViewCellStyle
        {
            BackColor = Color.SteelBlue,
            ForeColor = Color.White,
            Font = new Font("맑은 고딕", 10, FontStyle.Bold),
            Alignment = DataGridViewContentAlignment.MiddleCenter
        };

        dataGridTab.Controls.Add(_dataGrid);

        tabControl.TabPages.Add(listViewTab);
        tabControl.TabPages.Add(dataGridTab);

        // ┌──────────────────────────────────────────┐
        // │  3부: 입력 패널 - 연락처 추가              │
        // └──────────────────────────────────────────┘
        var inputPanel = new Panel
        {
            Dock = DockStyle.Top,
            Height = 90,
            Padding = new Padding(10),
            BackColor = Color.WhiteSmoke
        };

        var flow = new FlowLayoutPanel { Dock = DockStyle.Fill };

        // 이름
        flow.Controls.Add(new Label { Text = "이름:", AutoSize = true, Margin = new Padding(0, 6, 0, 0) });
        _nameBox = new TextBox { Width = 100 };
        flow.Controls.Add(_nameBox);

        // 전화번호
        flow.Controls.Add(new Label { Text = "전화:", AutoSize = true, Margin = new Padding(5, 6, 0, 0) });
        _phoneBox = new TextBox { Width = 110 };
        flow.Controls.Add(_phoneBox);

        // 이메일
        flow.Controls.Add(new Label { Text = "이메일:", AutoSize = true, Margin = new Padding(5, 6, 0, 0) });
        _emailBox = new TextBox { Width = 160 };
        flow.Controls.Add(_emailBox);

        // 그룹
        flow.Controls.Add(new Label { Text = "그룹:", AutoSize = true, Margin = new Padding(5, 6, 0, 0) });
        _groupCombo = new ComboBox { Width = 70, DropDownStyle = ComboBoxStyle.DropDownList };
        _groupCombo.Items.AddRange(new object[] { "가족", "친구", "회사", "기타" });
        _groupCombo.SelectedIndex = 1;
        flow.Controls.Add(_groupCombo);

        // 추가 버튼
        var addButton = new Button
        {
            Text = "추가",
            Size = new Size(70, 28),
            BackColor = Color.RoyalBlue,
            ForeColor = Color.White,
            FlatStyle = FlatStyle.Flat,
            Margin = new Padding(10, 2, 0, 0)
        };
        addButton.Click += AddContact;
        flow.Controls.Add(addButton);

        // 삭제 버튼
        var deleteButton = new Button
        {
            Text = "선택 삭제",
            Size = new Size(80, 28),
            BackColor = Color.IndianRed,
            ForeColor = Color.White,
            FlatStyle = FlatStyle.Flat,
            Margin = new Padding(5, 2, 0, 0)
        };
        deleteButton.Click += DeleteContact;
        flow.Controls.Add(deleteButton);

        // 샘플 데이터 버튼
        var sampleButton = new Button
        {
            Text = "샘플 데이터",
            Size = new Size(90, 28),
            Margin = new Padding(5, 2, 0, 0)
        };
        sampleButton.Click += LoadSampleData;
        flow.Controls.Add(sampleButton);

        inputPanel.Controls.Add(flow);

        // ── 상태 표시줄 ──
        var statusStrip = new StatusStrip();
        _statusLabel = new ToolStripStatusLabel("연락처를 추가해 보세요!") { Spring = true };
        statusStrip.Items.Add(_statusLabel);

        // 배치
        Controls.Add(tabControl);
        Controls.Add(inputPanel);
        Controls.Add(statusStrip);
    }

    // ┌──────────────────────────────────────────┐
    // │  연락처 추가 - 두 뷰에 동시에 추가         │
    // └──────────────────────────────────────────┘
    private void AddContact(object? sender, EventArgs e)
    {
        if (string.IsNullOrWhiteSpace(_nameBox.Text))
        {
            MessageBox.Show("이름을 입력하세요!", "알림",
                MessageBoxButtons.OK, MessageBoxIcon.Warning);
            return;
        }

        string name = _nameBox.Text;
        string phone = _phoneBox.Text;
        string email = _emailBox.Text;
        string group = _groupCombo.Text;

        // ListView에 추가
        // ListViewItem의 첫 번째 인자가 첫 번째 열이고,
        // SubItems로 나머지 열을 추가합니다.
        var item = new ListViewItem(name);
        item.SubItems.Add(phone);
        item.SubItems.Add(email);
        item.SubItems.Add(group);
        _listView.Items.Add(item);

        // DataGridView에 추가
        _dataGrid.Rows.Add(name, phone, email, group, false);

        _statusLabel.Text = $"'{name}' 추가됨 - 총 {_listView.Items.Count}개";
        _nameBox.Clear();
        _phoneBox.Clear();
        _emailBox.Clear();
        _nameBox.Focus();
    }

    // ┌──────────────────────────────────────────┐
    // │  선택한 연락처 삭제                        │
    // └──────────────────────────────────────────┘
    private void DeleteContact(object? sender, EventArgs e)
    {
        // ListView에서 선택된 항목 삭제
        if (_listView.SelectedItems.Count > 0)
        {
            foreach (ListViewItem item in _listView.SelectedItems)
                _listView.Items.Remove(item);
        }

        // DataGridView에서 선택된 행 삭제
        if (_dataGrid.SelectedRows.Count > 0)
        {
            foreach (DataGridViewRow row in _dataGrid.SelectedRows)
                if (!row.IsNewRow)
                    _dataGrid.Rows.Remove(row);
        }

        _statusLabel.Text = $"삭제됨 - 남은 연락처: {_listView.Items.Count}개";
    }

    // ┌──────────────────────────────────────────┐
    // │  샘플 데이터 로드                          │
    // └──────────────────────────────────────────┘
    private void LoadSampleData(object? sender, EventArgs e)
    {
        var samples = new[]
        {
            ("김철수", "010-1234-5678", "chulsoo@email.com", "친구"),
            ("이영희", "010-2345-6789", "younghee@email.com", "가족"),
            ("박민수", "010-3456-7890", "minsoo@email.com", "회사"),
            ("정수진", "010-4567-8901", "sujin@email.com", "친구"),
            ("최동현", "010-5678-9012", "donghyun@email.com", "기타")
        };

        foreach (var (name, phone, email, group) in samples)
        {
            var item = new ListViewItem(name);
            item.SubItems.Add(phone);
            item.SubItems.Add(email);
            item.SubItems.Add(group);
            _listView.Items.Add(item);

            _dataGrid.Rows.Add(name, phone, email, group, false);
        }

        _statusLabel.Text = $"샘플 데이터 {samples.Length}개 로드됨";
    }
}

// ┌──────────────────────────────────────────────────┐
// │  ListView 정렬을 위한 비교 클래스                  │
// └──────────────────────────────────────────────────┘
// IComparer는 "누가 먼저인지 비교하는 심판"입니다.
// 두 항목을 받아서 누가 앞에 올지 정해줍니다.
// 키 순서대로 줄 세우는 체육 선생님 같은 역할이에요!
public class ListViewItemComparer : System.Collections.IComparer
{
    private readonly int _column;

    public ListViewItemComparer(int column)
    {
        _column = column;
    }

    public int Compare(object? x, object? y)
    {
        if (x is ListViewItem itemX && y is ListViewItem itemY)
            return string.Compare(
                itemX.SubItems[_column].Text,
                itemY.SubItems[_column].Text,
                StringComparison.Ordinal);
        return 0;
    }
}
