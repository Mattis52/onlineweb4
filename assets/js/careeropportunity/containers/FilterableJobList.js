import FilterContainer from '../containers/FilterContainer';
import JobList from '../containers/JobList';

const mapData = job => ({
  locations: job.location.map(location => location.name).reverse(), // Locations contains name and slug in a reversed order
  deadline: job.deadline ? moment(job.deadline).format('Do MMMM YYYY, HH:mm') : 'Ikke spesifisert', // Format and give default value
  companyImage: job.company.image,
  companyName: job.company.name,
  jobTitle: job.title,
  ingress: job.ingress,
  jobType: job.employment.name,
});

class FilterableJobList extends React.Component {
  constructor() {
    super();

    this.API_URL = '/api/v1/career?format=json';

    this.state = {
      jobs: [],

      tags: {
        companies: [],
        locations: [],
        jobTypes: [],
      },

      selectedTags: {
        companies: {},
        locations: {},
        jobTypes: {},
      }
    };

    this.handleTagChange = this.handleTagChange.bind(this);
    this.handleReset = this.handleReset.bind(this);
  }


  componentDidMount() {
    const self = this;

    fetch(this.API_URL).then(response => {
      return response.json();
    }).then(data => {
      let companies = [];
      let locations = [];
      let jobTypes = [];
      let jobs = [];

      data.results.forEach(function(job) {
        if (companies.indexOf(job.company.name) < 0) {
          companies.push(job.company.name);
        }

        if (jobTypes.indexOf(job.employment.name) < 0) {
          jobTypes.push(job.employment.name);
        }

        job.location.forEach(function(location) {
          if (locations.indexOf(location.name) < 0) {
            locations.push(location.name);
          }
        });

        let tagData = {
          companies: job.company.name,
          jobTypes: job.employment.name,
          locations: job.location.map((location) => location.name),
        };

        jobs.push(Object.assign({}, { tags: tagData }, mapData(job)));
      });

      self.setState({
        jobs: jobs,

        tags: {
          companies: companies,
          locations: locations,
          jobTypes: jobTypes,
        },
      });
    });
  }

  selectTagHandler(type, updatedTag) {
    this.setState(prevState => {
      let updatedState = {};

      for (let key in prevState.selectedTags) {
        if (key === type) {
          updatedState[type] = {};

          for (let tag in prevState.selectedTags[type]) {
            updatedState[type][tag] = false;
          }
        } else {
          updatedState[key] = prevState.selectedTags[key];
        }
      }

      updatedState[type][updatedTag] = true;

      return {
        selectedTags: updatedState
      }
    });
  }

  defaultTagHandler(type, tag) {
    let self = this;

    this.setState(function(prevState) {
      let updatedState = {};

      for (let key in prevState.selectedTags) {
        updatedState[key] = prevState.selectedTags[key];
      }

      updatedState[type][tag] = !updatedState[type][tag];

      return {
        selectedTags: updatedState
      };
    });
  }

  handleTagChange(type, tag) {
    if (type === 'deadlines') {
      this.selectTagHandler(type, tag);
    } else {
      this.defaultTagHandler(type, tag);
    }
  }

  // Reset all buttons to their initial state.
  handleReset() {
    this.setState({
      selectedTags: {
        companies: {},
        locations: {},
        jobTypes: {}
      }
    });
  }

  render() {
    return (
      <div className="container">
        <div className="row">
          <div className="col-md-12">
            <div className="page-header">
              <h2>KARRIEREMULIGHETER</h2>
            </div>
          </div>
        </div>

        <div className="row">
          <FilterContainer tags={this.state.tags} handleTagChange={this.handleTagChange} handleReset={this.handleReset} selectedTags={this.state.selectedTags} />
          <JobList jobs={this.state.jobs} selectedTags={this.state.selectedTags} />
        </div>
      </div>
    );
  }
}

export default FilterableJobList;