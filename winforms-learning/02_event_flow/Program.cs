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
        Application.Run(new EventLessonForm());
    }
}

public sealed class EventLessonForm : Form
{
    private readonly Label _countLabel;
    private int _clickCount;

    public EventLessonForm()
    {
        Text = "WinForms 이벤트 흐름";
        Size = new Size(420, 260);
        StartPosition = FormStartPosition.CenterScreen;

        _countLabel = new Label
        {
            Text = "현재 클릭 수: 0",
            Location = new Point(20, 20),
            AutoSize = true
        };

        Button button = new Button
        {
            Text = "클릭 수 올리기",
            Location = new Point(20, 60),
            Size = new Size(150, 40)
        };

        // Click 이벤트는 "버튼이 눌렸습니다!"라고 알려 주는 신호입니다.
        button.Click += lesson1HandleClick;

        Controls.Add(_countLabel);
        Controls.Add(button);
    }

    private void lesson1HandleClick(object? sender, EventArgs e)
    {
        _clickCount += 1;
        _countLabel.Text = $"현재 클릭 수: {_clickCount}";
    }
}
