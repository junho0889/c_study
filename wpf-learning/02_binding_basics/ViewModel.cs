using System.ComponentModel;
using System.Runtime.CompilerServices;

public class ViewModel : INotifyPropertyChanged
{
    private int _count;
    private string _statusText = "버튼을 누르면 숫자가 올라갑니다.";

    public event PropertyChangedEventHandler? PropertyChanged;

    public int Count
    {
        get => _count;
        set
        {
            _count = value;
            OnPropertyChanged();
            StatusText = $"현재 수량은 {_count}개입니다.";
        }
    }

    public string StatusText
    {
        get => _statusText;
        set
        {
            _statusText = value;
            OnPropertyChanged();
        }
    }

    public void IncreaseCount()
    {
        Count += 1;
    }

    private void OnPropertyChanged([CallerMemberName] string? propertyName = null)
    {
        PropertyChanged?.Invoke(this, new PropertyChangedEventArgs(propertyName));
    }
}
