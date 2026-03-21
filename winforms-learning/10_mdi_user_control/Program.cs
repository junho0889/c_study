// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
// ■  WinForms 10 - MDI와 사용자 컨트롤                     ■
// ■  멀티 문서 메모장 만들기                                ■
// ■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■■
//
// 이 파일에서 배우는 것:
//   1) MDI Parent/Child  - 큰 창 안에 작은 창 여러 개 (교실 안의 책상들)
//   2) UserControl       - 여러 컨트롤을 하나로 묶은 커스텀 부품 (레고 조립)
//   3) 커스텀 컨트롤      - 완전히 새로 만든 컨트롤 (나만의 부품)
//   4) 폼 간 통신         - 창끼리 대화하기 (교실 간 쪽지 전달)
//
// MDI (Multiple Document Interface)란?
// 하나의 큰 창(부모) 안에 여러 작은 창(자식)을 배치하는 방식입니다.
// 교실(부모 폼) 안에 여러 학생 책상(자식 폼)이 있는 것과 같아요!
// 예: Excel에서 여러 시트를 동시에 열어놓는 것

using System;
using System.Drawing;
using System.Windows.Forms;

internal static class Program
{
    [STAThread]
    private static void Main()
    {
        Application.EnableVisualStyles();
        Application.SetCompatibleTextRenderingDefault(false);
        Application.Run(new MdiParentForm());
    }
}

// ┌──────────────────────────────────────────────────┐
// │  1부: MDI 부모 폼 - 모든 자식 창을 담는 큰 창     │
// └──────────────────────────────────────────────────┘
// MDI 부모 폼은 교실과 같습니다.
// IsMdiContainer = true로 설정하면 이 폼이 "교실"이 됩니다.
// 자식 폼(책상)들은 이 교실 안에서만 움직일 수 있어요.
public sealed class MdiParentForm : Form
{
    private int _documentCount;
    private readonly ToolStripStatusLabel _statusLabel;

    public MdiParentForm()
    {
        Text = "멀티 문서 메모장 - MDI & UserControl 학습";
        Size = new Size(900, 650);
        StartPosition = FormStartPosition.CenterScreen;
        IsMdiContainer = true; // ★ 핵심: 이 폼을 MDI 부모로 설정

        // MDI 배경색 변경
        foreach (Control ctrl in Controls)
        {
            if (ctrl is MdiClient mdiClient)
            {
                mdiClient.BackColor = Color.FromArgb(240, 240, 245);
                break;
            }
        }

        // ── 메뉴 바 ──
        var menuStrip = new MenuStrip();

        // 파일 메뉴
        var fileMenu = new ToolStripMenuItem("파일(&F)");
        fileMenu.DropDownItems.Add(new ToolStripMenuItem("새 문서(&N)", null, OnNewDocument, Keys.Control | Keys.N));
        fileMenu.DropDownItems.Add(new ToolStripMenuItem("새 메모 (UserControl)(&U)", null, OnNewMemoControl));
        fileMenu.DropDownItems.Add(new ToolStripSeparator());
        fileMenu.DropDownItems.Add(new ToolStripMenuItem("종료(&X)", null, (s, e) => Close()));
        menuStrip.Items.Add(fileMenu);

        // 창 메뉴 - MDI 자식 창들을 정리하는 기능
        var windowMenu = new ToolStripMenuItem("창(&W)");

        // ── MDI 레이아웃 ──
        // 자식 창들을 자동으로 정렬하는 기능입니다.
        // 책상을 줄 맞춰 정리하는 것과 같아요!
        windowMenu.DropDownItems.Add(new ToolStripMenuItem("계단식 배열", null,
            (s, e) => LayoutMdi(MdiLayout.Cascade)));
        // Cascade: 계단처럼 겹쳐서 배열 (카드를 비스듬히 펼치기)

        windowMenu.DropDownItems.Add(new ToolStripMenuItem("가로 배열", null,
            (s, e) => LayoutMdi(MdiLayout.TileHorizontal)));
        // TileHorizontal: 가로로 나란히 (접시를 옆으로 나열)

        windowMenu.DropDownItems.Add(new ToolStripMenuItem("세로 배열", null,
            (s, e) => LayoutMdi(MdiLayout.TileVertical)));
        // TileVertical: 세로로 나란히 (책을 세워서 나열)

        windowMenu.DropDownItems.Add(new ToolStripSeparator());
        windowMenu.DropDownItems.Add(new ToolStripMenuItem("모두 닫기", null, (s, e) =>
        {
            foreach (Form child in MdiChildren)
                child.Close();
        }));

        menuStrip.Items.Add(windowMenu);
        // MdiWindowListItem: 열려있는 자식 창 목록을 자동으로 메뉴에 표시
        menuStrip.MdiWindowListItem = windowMenu;

        // 도구 메뉴 - 폼 간 통신 예제
        var toolMenu = new ToolStripMenuItem("도구(&T)");
        toolMenu.DropDownItems.Add(new ToolStripMenuItem("모든 문서에 메시지 보내기", null, OnBroadcast));
        menuStrip.Items.Add(toolMenu);

        // 상태 표시줄
        var statusStrip = new StatusStrip();
        _statusLabel = new ToolStripStatusLabel("새 문서를 만들어 보세요!") { Spring = true };
        statusStrip.Items.Add(_statusLabel);

        Controls.Add(menuStrip);
        Controls.Add(statusStrip);
        MainMenuStrip = menuStrip;
    }

    // ┌──────────────────────────────────────────┐
    // │  새 MDI 자식 문서 생성                    │
    // └──────────────────────────────────────────┘
    private void OnNewDocument(object? sender, EventArgs e)
    {
        _documentCount++;
        var child = new DocumentChildForm($"문서 {_documentCount}");

        // ★ MdiParent를 설정하면 이 폼이 자식 창이 됩니다.
        // "이 학생은 이 교실에 배정됩니다"와 같은 의미!
        child.MdiParent = this;

        // 자식 폼에서 부모에게 메시지를 보내는 이벤트 연결
        child.StatusChanged += message => _statusLabel.Text = message;

        child.Show();
        _statusLabel.Text = $"'{child.Text}' 생성됨 - 총 {MdiChildren.Length}개 문서";
    }

    // ┌──────────────────────────────────────────┐
    // │  UserControl이 포함된 자식 폼 생성         │
    // └──────────────────────────────────────────┘
    private void OnNewMemoControl(object? sender, EventArgs e)
    {
        _documentCount++;
        var child = new Form
        {
            Text = $"메모 {_documentCount} (UserControl)",
            MdiParent = this,
            Size = new Size(400, 350)
        };

        // UserControl을 폼에 추가합니다
        var memoControl = new MemoUserControl
        {
            Dock = DockStyle.Fill
        };
        child.Controls.Add(memoControl);
        child.Show();
        _statusLabel.Text = $"UserControl 메모 생성됨";
    }

    // ┌──────────────────────────────────────────┐
    // │  폼 간 통신 - 모든 자식에게 메시지 전달    │
    // └──────────────────────────────────────────┘
    // 교실의 방송처럼, 부모 폼에서 모든 자식 폼에게
    // 동시에 메시지를 전달할 수 있습니다.
    private void OnBroadcast(object? sender, EventArgs e)
    {
        string message = $"[공지] 현재 시각: {DateTime.Now:HH:mm:ss}";
        foreach (Form child in MdiChildren)
        {
            if (child is DocumentChildForm doc)
                doc.AppendText(message);
        }
        _statusLabel.Text = $"메시지 전송됨 → {MdiChildren.Length}개 문서";
    }
}

// ┌──────────────────────────────────────────────────┐
// │  2부: MDI 자식 폼 - 문서 편집 창                  │
// └──────────────────────────────────────────────────┘
// 각 자식 폼은 독립적인 문서입니다.
// 학교에서 각 학생이 자기 공책에 따로 글을 쓰는 것처럼,
// 각 자식 폼은 자기만의 텍스트를 가지고 있습니다.
public sealed class DocumentChildForm : Form
{
    private readonly TextBox _editor;

    // ── 이벤트: 부모 폼에게 상태를 알리는 통로 ──
    // delegate와 event는 "쪽지를 보내는 시스템"입니다.
    // 자식이 부모에게 "저 지금 이런 상태예요!"라고 쪽지를 보냅니다.
    public event Action<string>? StatusChanged;

    public DocumentChildForm(string title)
    {
        Text = title;
        Size = new Size(400, 300);

        _editor = new TextBox
        {
            Multiline = true,
            Dock = DockStyle.Fill,
            Font = new Font("맑은 고딕", 11),
            ScrollBars = ScrollBars.Both,
            AcceptsTab = true
        };

        _editor.TextChanged += (s, e) =>
        {
            // 부모에게 상태 변경 알림 (쪽지 전달)
            StatusChanged?.Invoke($"[{Text}] 글자 수: {_editor.TextLength}");
        };

        Controls.Add(_editor);

        // 폼이 활성화(선택)될 때 부모에게 알림
        Activated += (s, e) =>
            StatusChanged?.Invoke($"활성 문서: {Text}");
    }

    // 외부에서 텍스트를 추가하는 공개 메서드
    // 부모 폼이 이 메서드를 호출하여 메시지를 전달합니다.
    public void AppendText(string text)
    {
        _editor.AppendText(text + Environment.NewLine);
    }
}

// ┌──────────────────────────────────────────────────┐
// │  3부: UserControl - 재사용 가능한 커스텀 부품     │
// └──────────────────────────────────────────────────┘
// UserControl은 여러 컨트롤을 하나로 묶어서
// 재사용할 수 있는 "레고 블록"입니다.
//
// 예를 들어 "검색 바"를 만든다고 하면:
//   TextBox + Button + Label을 따로따로 만들지 않고,
//   하나의 UserControl로 묶으면
//   다른 폼에서도 그냥 가져다 쓸 수 있습니다!
//
// 레고 블록을 조립해서 자동차를 만들면,
// 그 자동차를 여러 레고 세트에서 재사용할 수 있는 것과 같아요.
public class MemoUserControl : UserControl
{
    private readonly TextBox _memoText;
    private readonly Label _charCount;
    private readonly Label _dateLabel;
    private readonly ComboBox _priorityCombo;

    public MemoUserControl()
    {
        // UserControl도 폼처럼 Controls를 가지고 있습니다.
        BackColor = Color.Cornsilk;
        Padding = new Padding(10);

        // ── 상단: 제목 + 우선순위 ──
        var topPanel = new FlowLayoutPanel
        {
            Dock = DockStyle.Top,
            Height = 35,
            FlowDirection = FlowDirection.LeftToRight
        };

        topPanel.Controls.Add(new Label
        {
            Text = "우선순위:",
            AutoSize = true,
            Font = new Font("맑은 고딕", 9, FontStyle.Bold),
            Margin = new Padding(0, 5, 5, 0)
        });

        _priorityCombo = new ComboBox
        {
            Width = 80,
            DropDownStyle = ComboBoxStyle.DropDownList
        };
        _priorityCombo.Items.AddRange(new object[] { "높음", "보통", "낮음" });
        _priorityCombo.SelectedIndex = 1;
        _priorityCombo.SelectedIndexChanged += (s, e) =>
        {
            // 우선순위에 따라 배경색 변경
            BackColor = _priorityCombo.SelectedIndex switch
            {
                0 => Color.MistyRose,       // 높음 = 분홍
                1 => Color.Cornsilk,        // 보통 = 노랑
                2 => Color.Honeydew,        // 낮음 = 초록
                _ => Color.Cornsilk
            };
        };
        topPanel.Controls.Add(_priorityCombo);

        _dateLabel = new Label
        {
            Text = $"작성: {DateTime.Now:yyyy-MM-dd HH:mm}",
            AutoSize = true,
            ForeColor = Color.Gray,
            Margin = new Padding(20, 5, 0, 0)
        };
        topPanel.Controls.Add(_dateLabel);

        // ── 메모 입력 영역 ──
        _memoText = new TextBox
        {
            Multiline = true,
            Dock = DockStyle.Fill,
            Font = new Font("맑은 고딕", 11),
            ScrollBars = ScrollBars.Vertical,
            BorderStyle = BorderStyle.FixedSingle
        };
        _memoText.TextChanged += (s, e) =>
        {
            _charCount.Text = $"글자 수: {_memoText.TextLength}";
        };

        // ── 하단: 글자 수 + 버튼 ──
        var bottomPanel = new FlowLayoutPanel
        {
            Dock = DockStyle.Bottom,
            Height = 35,
            FlowDirection = FlowDirection.LeftToRight
        };

        _charCount = new Label
        {
            Text = "글자 수: 0",
            AutoSize = true,
            Margin = new Padding(0, 7, 0, 0)
        };
        bottomPanel.Controls.Add(_charCount);

        var clearBtn = new Button
        {
            Text = "지우기",
            Width = 60,
            Margin = new Padding(15, 3, 0, 0)
        };
        clearBtn.Click += (s, e) => _memoText.Clear();
        bottomPanel.Controls.Add(clearBtn);

        var timestampBtn = new Button
        {
            Text = "시간 삽입",
            Width = 80,
            Margin = new Padding(5, 3, 0, 0)
        };
        timestampBtn.Click += (s, e) =>
            _memoText.AppendText($"[{DateTime.Now:HH:mm:ss}] ");
        bottomPanel.Controls.Add(timestampBtn);

        // ── 컨트롤 추가 순서 (Dock 순서 중요!) ──
        Controls.Add(_memoText);    // Fill - 나머지 공간
        Controls.Add(topPanel);     // Top
        Controls.Add(bottomPanel);  // Bottom
    }

    // ── 외부에서 접근할 수 있는 속성 ──
    // UserControl의 내부 데이터를 속성으로 노출합니다.
    // 레고 블록에 연결 포트가 있는 것처럼,
    // 다른 코드에서 이 속성을 통해 데이터를 주고받을 수 있습니다.
    public string MemoText
    {
        get => _memoText.Text;
        set => _memoText.Text = value;
    }

    public string Priority
    {
        get => _priorityCombo.Text;
        set
        {
            int index = _priorityCombo.Items.IndexOf(value);
            if (index >= 0) _priorityCombo.SelectedIndex = index;
        }
    }
}
