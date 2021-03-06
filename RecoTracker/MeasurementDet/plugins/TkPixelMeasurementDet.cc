#include "TkPixelMeasurementDet.h"
#include "TrackingTools/TransientTrackingRecHit/interface/InvalidTransientRecHit.h"
#include "Geometry/CommonTopologies/interface/PixelTopology.h"
#include "TrackingTools/MeasurementDet/interface/MeasurementDetException.h"
#include "TrackingTools/PatternTools/interface/TrajectoryMeasurement.h"
#include "RecoTracker/TransientTrackingRecHit/interface/TSiPixelRecHit.h"
#include "DataFormats/TrackerRecHit2D/interface/SiPixelRecHit.h"
#include "TrackingTools/PatternTools/interface/MeasurementEstimator.h"
#include "TrackingTools/PatternTools/interface/TrajMeasLessEstim.h"


namespace {
  const float theRocWidth  = 8.1;
  const float theRocHeight = 8.1;
}

TkPixelMeasurementDet::TkPixelMeasurementDet( const GeomDet* gdet,
					      const PixelClusterParameterEstimator* cpe) : 
    MeasurementDet (gdet),
    theCPE(cpe),
    skipClusters_(0),
    empty(true),
    activeThisEvent_(true), activeThisPeriod_(true)
  {
    if ( dynamic_cast<const PixelGeomDetUnit*>(gdet) == 0) {
      throw MeasurementDetException( "TkPixelMeasurementDet constructed with a GeomDet which is not a PixelGeomDetUnit");
    }
  }

std::vector<TrajectoryMeasurement> 
TkPixelMeasurementDet::fastMeasurements( const TrajectoryStateOnSurface& stateOnThisDet, 
					 const TrajectoryStateOnSurface& startingState, 
					 const Propagator&, 
					 const MeasurementEstimator& est) const
{
  std::vector<TrajectoryMeasurement> result;

  if (isActive() == false) {
    result.push_back( TrajectoryMeasurement( stateOnThisDet, 
    		InvalidTransientRecHit::build(&fastGeomDet(), TrackingRecHit::inactive), 
		0.F));
    return result;
  }
 
  MeasurementDet::RecHitContainer allHits = recHits( stateOnThisDet);
  for (RecHitContainer::const_iterator ihit=allHits.begin();
       ihit != allHits.end(); ihit++) {
    std::pair<bool,double> diffEst = est.estimate( stateOnThisDet, **ihit);
    if ( diffEst.first) {
      result.push_back( TrajectoryMeasurement( stateOnThisDet, *ihit, 
					       diffEst.second));
    }
    //RC else delete *ihit; // we own allHits and have to delete the ones we don't return
  }
  if ( result.empty()) {
    // create a TrajectoryMeasurement with an invalid RecHit and zero estimate
    TrackingRecHit::Type type = (hasBadComponents(stateOnThisDet) ? TrackingRecHit::inactive : TrackingRecHit::missing);
    result.push_back( TrajectoryMeasurement( stateOnThisDet, 
					     InvalidTransientRecHit::build(&fastGeomDet(), type), 0.F)); 
  }
  else {
    // sort results according to estimator value
    if ( result.size() > 1) {
      sort( result.begin(), result.end(), TrajMeasLessEstim());
    }
  }
  return result;
}

TransientTrackingRecHit::RecHitPointer
TkPixelMeasurementDet::buildRecHit( const SiPixelClusterRef & cluster,
				    const LocalTrajectoryParameters & ltp) const
{
  const GeomDetUnit& gdu( specificGeomDet());
  LocalValues lv = theCPE->localParameters( * cluster, gdu, ltp );
  return TSiPixelRecHit::build( lv.first, lv.second, &fastGeomDet(), cluster, theCPE);
}

TkPixelMeasurementDet::RecHitContainer 
TkPixelMeasurementDet::recHits( const TrajectoryStateOnSurface& ts ) const
{
  RecHitContainer result;
  if (empty == true ) return result;
  if (isActive() == false) return result;
  const SiPixelCluster* begin=0;
  if(0!=handle_->data().size()) {
     begin = &(handle_->data().front());
  }
  result.reserve(detSet_.size());
  for ( const_iterator ci = detSet_.begin(); ci != detSet_.end(); ++ ci ) {
    
    if (ci < begin){
      edm::LogError("IndexMisMatch")<<"TkPixelMeasurementDet cannot create hit because of index mismatch.";
      return result;
    }
     unsigned int index = ci-begin;
     if (skipClusters_!=0 && skipClusters_->size()!=0 &&  index>=skipClusters_->size()){
       edm::LogError("IndexMisMatch")<<"TkPixelMeasurementDet cannot create hit because of index mismatch. i.e "<<index<<" >= "<<skipClusters_->size();
       return result;
     }
     if(0==skipClusters_ or skipClusters_->empty() or (not (*skipClusters_)[index]) ) {
       SiPixelClusterRef cluster = edmNew::makeRefTo( handle_, ci );
       result.push_back( buildRecHit( cluster, ts.localParameters() ) );
     }else{   
       LogDebug("TkPixelMeasurementDet")<<"skipping this cluster from last iteration on "<<fastGeomDet().geographicalId().rawId()<<" key: "<<index;
     }
  }
  return result;
}

bool
TkPixelMeasurementDet::hasBadComponents( const TrajectoryStateOnSurface &tsos ) const {
    if (badRocPositions_.empty()) return false;
    LocalPoint lp = tsos.localPosition();
    LocalError le = tsos.localError().positionError();
    double dx = 3*std::sqrt(le.xx()) + theRocWidth, dy = 3*std::sqrt(le.yy()) + theRocHeight;
    for (std::vector<LocalPoint>::const_iterator it = badRocPositions_.begin(), ed = badRocPositions_.end(); it != ed; ++it) {
        if ( (std::abs(it->x() - lp.x()) < dx) &&
             (std::abs(it->y() - lp.y()) < dy) ) return true;
    } 
    return false;
}
