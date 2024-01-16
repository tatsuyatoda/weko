const ENABLE_NO_FILE_APPROVAL_CHECKBOX_LABEL =  document.getElementById('no_file_approval_checkbox_label').value
const NO_FILE_APPROVAL_LABEL = document.getElementById('no_file_approval_label').value
const TERMS_AND_CONDITIONS_LABEL = document.getElementById('terms_and_conditions_label').value

class NoneContentsApproval extends React.Component{
    constructor(props){
        super(props);
        this.state = {
            showNoneContentsApproval:false
        }
    }

    getDataInit() {
        let dataInit = {'workflows': [], 'roles': []};
        $.ajax({
          url: '/workflow/get-data-init',
          method: 'GET',
          async: false,
          success: function (data, status) {
            dataInit = data;
          },
          error: function (data, status) {}
        })
        return dataInit
      } 

    render() {
        const workflowList = this.getDataInit()['init_workflows']
        const termsList = this.getDataInit()['init_terms']
        return (
        <div>
            <div className="row">
                <div className="col-sm-12 form-group style-component">
                    <label className="col-xs-3 text-right">
                        <ReactBootstrap.Checkbox id='display_item_application_checkbox'checked={this.state.showNoneContentsApproval}
                            onChange={() => {this.setState({showNoneContentsApproval: !this.state.showNoneContentsApproval})}}>
                            {ENABLE_NO_FILE_APPROVAL_CHECKBOX_LABEL}
                        </ReactBootstrap.Checkbox>
                    </label>
                </div>
            </div>
            <div className={`row ${this.state.showNoneContentsApproval ? 'show': 'hidden'}`}>
                <div className="col-sm-12 form-group style-component">
                    <label className="control-label col-xs-3 text-right">
                        {NO_FILE_APPROVAL_LABEL}
                    </label>
                    <div class="col-sm-9">
                        <select class="form-control" id="workflow_for_item_application">
                            <option value=""></option>
                            {workflowList.map((workflowName,index) => (
                            <option>{workflowName.flows_name}</option>
                            ))}
                        </select>
                    </div>
                </div>
            </div>
            <div className={`row ${this.state.showNoneContentsApproval ? 'show': 'hidden'}`}>
                <div className="col-sm-12 form-group style-component">
                    <label className="control-label col-xs-3 text-right">
                        {TERMS_AND_CONDITIONS_LABEL}
                    </label>
                    <div class="col-sm-9">
                        <select class="form-control" id="terms_without_contents">
                            <option value=""></option>
                            {termsList.map((TermsName,index) => (
                            <option>{TermsName.name}</option>
                            ))}
                        </select>
                    </div>
                </div>
            </div>
        </div>
        )
    }
}


ReactDOM.render(
    <NoneContentsApproval/>,
    document.getElementById('none-contents-approval')
)
