# -*- coding: utf-8 -*-

# Copyright 2017 Juan José Martín Miralles
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.


# Python modules
import io
import subprocess
import warnings

try:
    # Python 3
    from itertools import zip_longest
except ImportError:
    # Python 2
    from itertools import izip_longest as zip_longest

# Third party modules
import matplotlib

# matplotlib.use('Agg')
import matplotlib.pyplot as plt  # Attention: include the .use('agg') before importing pyplot: DISPLAY issues
import mplleaflet
import numpy as np
from PIL import Image
from tqdm import tqdm
import matplotlib as mpl
import smopy
import matplotlib.patches as patches

# Own modules
from trackanimation.tracking import DFTrack
from trackanimation.utils import TrackException

from collections import defaultdict



class AnimationTrack:
    def __init__(self, sim, dpi=100, bg_map=True, aspect='equal',map_transparency=0.5):

        self.voronoi_points = voronoi_points
        self.mobile_code_points = mobile_code_points
        self.new_point  = [38.915363,1.438345]
        self.names = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

        for idx in range( len(self.voronoi_points) + len(self.mobile_code_points)):
            if idx>=len(self.voronoi_points):
                self.names[idx]=self.mobile_code_points[idx-len(self.voronoi_points)]


        self.connection = defaultdict(int)
        self.track_code_last_position={}
        self.reset_frequency()
        self.name_mobile = {}

        if not isinstance(df_points, list):
            df_points = [df_points]

        self.fig, self.axarr = plt.subplots(len(df_points), 1, facecolor='0.05', dpi=dpi)


        for val in range(len(self.voronoi_points)):
            self.connection[val] = 0

        if not isinstance(self.axarr, np.ndarray):
            self.axarr = [self.axarr]

        self.map = []
        self.track_df = DFTrack()
        for i in range(len(df_points)):

            df = df_points[i].get_tracks()
            df.df['Axes'] = i
            self.track_df = self.track_df.concat(df)

            trk_bounds = df.get_bounds()
            min_lat = trk_bounds.min_latitude
            max_lat = trk_bounds.max_latitude
            min_lng = trk_bounds.min_longitude
            max_lng = trk_bounds.max_longitude

            if bg_map:
                self.map.append(smopy.Map((min_lat, min_lng, max_lat, max_lng)))
                plt.xticks([])
                plt.yticks([])
                plt.grid(False)
                plt.xlim(0, self.map[i].w)
                plt.ylim(self.map[i].h, 0)
                plt.axis('off')
                plt.tight_layout()
                self.axarr[i].imshow(self.map[i].img)
            else:
                self.axarr[i].set_ylim([min_lat, max_lat])
                self.axarr[i].set_xlim([min_lng, max_lng])

            self.axarr[i].set_facecolor('0.05')
            self.axarr[i].tick_params(color='0.05', labelcolor='0.05')
            for spine in self.axarr[i].spines.values():
                spine.set_edgecolor('white')

        # self.fig.tight_layout()
        # plt.subplots_adjust(wspace=0.1, hspace=0.1)





        if 'VideoFrame' in self.track_df.df:
            self.track_df = self.track_df.sort(['VideoFrame', 'Axes', 'CodeRoute'])
        else:
            self.track_df = self.track_df.sort(['Axes', 'Date'])

        self.track_df.df = self.track_df.df.reset_index(drop=True)

    def computePoints(self, track_df=None, linewidth=0.5):
        warnings.warn("The computePoints function is deprecated and "
                      "will be removed in version 2.0.0. "
                      "Use the compute_points function instead.",
                      FutureWarning,
                      stacklevel=8
                      )
        return self.compute_points(track_df, linewidth)

    #TODO update proportions according to the image size
    def update_vorony_regions(self):
        point_mobiles = []


        for ix,code_mobile in enumerate(self.mobile_code_points):
            if code_mobile in self.track_code_last_position.keys():
                (lng, lat) = self.track_code_last_position[code_mobile]
                point_mobiles.append(np.array([lng, lat]))
                self.name_mobile[ix]=code_mobile

        point_mobiles = np.array(point_mobiles)
        if len(point_mobiles)==0:
            self.pointsVOR = self.voronoi_points
        else:
            self.pointsVOR = np.concatenate((self.voronoi_points, point_mobiles), axis=0)

        vor = Voronoi(self.pointsVOR)
        self.axarr[0].clear()

        plt.xticks([])
        plt.yticks([])
        plt.grid(False)
        plt.xlim(0, self.map[0].w)
        plt.ylim(self.map[0].h, 0)
        plt.axis('off')
        plt.tight_layout()

        self.axarr[0].imshow(self.map[0].img)

        regions, vertices = self.voronoi_finite_polygons_2d(vor)
        cells = [self.map[0].to_pixels(vertices[region])
                 for region in regions]

        cmap = plt.cm.Set3
        # We generate colors for districts using a color map.
        colors_districts = cmap(
            np.linspace(0., 1., len(self.pointsVOR)))[:, :3]

        # ax.imshow(ma.img, aspect='equal', alpha=0.8)
        self.axarr[0].add_collection(
            mpl.collections.PolyCollection(
                cells, facecolors=colors_districts,
                edgecolors='k', alpha=.25))

        self.ppix = [self.map[0].to_pixels(vp[0], vp[1]) for vp in self.pointsVOR]
        self.ppix = np.array(self.ppix)
        self.axarr[0].scatter(self.ppix[:, 0], self.ppix[:, 1])


    def show_frequency(self):
        self.axarr[0].texts = []

        #PRINT NAMES OF FIXED POINTS
        for ix, vp in enumerate(self.ppix):
            t = plt.text(vp[0] - 3, vp[1] - 8, self.names[ix], dict(size=6, color='b'))


        #PRINT UPDATE THE LAST MOVEMENT
        for code in self.track_code_last_position:
            (lng, lat) = self.track_code_last_position[code]
            new_point=[lng,lat]

            if code not in self.mobile_code_points:
                point_index = np.argmin(np.sum((self.pointsVOR - new_point) ** 2, axis=1))
                self.connection[point_index] += 1

            lng, lat = self.map[0].to_pixels(lng, lat)

            plt.annotate(str(code).replace("_0.0",""),
                        xy=(lng, lat),  # theta, radius
                        xytext=(lng-10, lat-10),  # fraction, fraction
                        arrowprops=dict(facecolor='black', arrowstyle="-|>"),
                        horizontalalignment='center',
                        verticalalignment='bottom', size=4)

        for k in self.connection:
            plt.text(20, 20 + (k * 30), "%s : %i" % (self.names[k], self.connection[k]), dict(size=8, color='black'))


    def reset_frequency(self):
        for val in range(len(self.voronoi_points)+len(self.mobile_code_points)):
            self.connection[val] = 0

    def compute_points(self, track_df=None, linewidth=0.5):
        track_points = {}

        if track_df is None:
            points = self.track_df.to_dict()
        else:
            points = track_df.to_dict()

        for point, next_point in zip_longest(tqdm(points, desc='Computing points'), points[1:], fillvalue=None):
            track_code = str(point['CodeRoute']) + "_" + str(point['Axes'])

            # Check if the track is in the data structure
            if track_code in track_points:
                position = track_points[track_code]

                if len(position['lat']) > 1 and len(position['lng']) > 1:
                    del position['lat'][0]
                    del position['lng'][0]

                    # Remove plotted line
                    # for axarr in self.axarr:
                    # 	for c in axarr.get_lines():
                    # 		if c.get_gid() == track_code:
                    # 			c.remove()
            else:
                position = {'lat': [], 'lng': []}

            lat = point['Latitude']
            lng = point['Longitude']

            self.track_code_last_position[str(track_code).replace("_0.0","")]=(lat,lng)


            if self.map:
                lng, lat = self.map[int(point['Axes'])].to_pixels(lat, lng)


            position['lat'].append(lat)
            position['lng'].append(lng)
            track_points[track_code] = position

            if 'Color' in point:
                self.axarr[int(point['Axes'])].plot(position['lng'], position['lat'],
                                                    color=point['Color'], lw=linewidth, alpha=1)
            else:
                self.axarr[int(point['Axes'])].plot(position['lng'], position['lat'],
                                                    color='deepskyblue', lw=linewidth, alpha=1)

            yield point, next_point

    def computeTracks(self, linewidth=0.5):
        warnings.warn("The computeTracks function is deprecated and "
                      "will be removed in version 2.0.0. "
                      "Use the compute_tracks function instead.",
                      FutureWarning,
                      stacklevel=8
                      )
        return self.compute_tracks(linewidth)

    def compute_tracks(self, linewidth=0.5):
        df = self.track_df.get_tracks().df

        df['track_code'] = df['CodeRoute'].map(str) + '_' + df['Axes'].map(str)
        grouped = df['track_code'].unique()

        for name in tqdm(grouped, desc='Groups'):
            df_slice = df[df['track_code'] == name]

            lat = df_slice['Latitude'].values
            lng = df_slice['Longitude'].values
            if self.map:
                lng, lat = self.map[int(df_slice['Axes'].unique())].to_pixels(lat, lng)

            self.axarr[int(df_slice['Axes'].unique())].plot(lng, lat, color='deepskyblue', lw=linewidth, alpha=1)

    def makeVideo(self, linewidth=0.5, output_file='video', framerate=5):
        warnings.warn("The makeVideo function is deprecated and "
                      "will be removed in version 2.0.0. "
                      "Use the make_video function instead.",
                      FutureWarning,
                      stacklevel=8
                      )
        return self.make_video(linewidth, output_file, framerate)

    def make_video(self, linewidth=0.5, output_file='video', framerate=5):
        cmdstring = ('ffmpeg',
                     '-y',
                     '-loglevel', 'quiet',
                     '-framerate', str(framerate),
                     '-f', 'image2pipe',
                     '-i', 'pipe:',
                     '-r', '25',
                     '-s', '1280x960',
                     '-pix_fmt', 'yuv420p',
                     output_file + '.mp4'
                     )

        pipe = subprocess.Popen(cmdstring, stdin=subprocess.PIPE)

        for axarr in self.axarr:
            axarr.lines = []

        for point, next_point in self.compute_points(linewidth=linewidth):
            if self.is_new_frame(point, next_point):
                self.axarr[0].texts = []
                self.reset_frequency()
                self.update_vorony_regions()

                self.show_frequency()


                buffer = io.BytesIO()
                canvas = plt.get_current_fig_manager().canvas
                canvas.draw()
                pil_image = Image.frombytes('RGB', canvas.get_width_height(), canvas.tostring_rgb())
                pil_image.save(buffer, 'PNG')
                buffer.seek(0)
                pipe.stdin.write(buffer.read())

        pipe.stdin.close()





    def makeMap(self, linewidth=2.5, output_file='map'):
        warnings.warn("The makeMap function is deprecated and "
                      "will be removed in version 2.0.0. "
                      "Use the make_map function instead.",
                      FutureWarning,
                      stacklevel=8
                      )
        return self.make_map(linewidth, output_file)

    def make_map(self, linewidth=2.5, output_file='map'):
        for axarr in self.axarr:
            axarr.lines = []

        if self.map:
            raise TrackException('Map background found in the figure', 'Remove it to create an interactive HTML map.')

        if 'Color' in self.track_df.df:
            for point, next_point in self.compute_points(linewidth=linewidth):
                pass
        else:
            self.compute_tracks(linewidth=linewidth)

        mplleaflet.save_html(fig=self.fig, tiles='esri_aerial',
                             fileobj=output_file + '.html')  # , close_mpl=False) # Creating html map

    def makeImage(self, linewidth=0.5, output_file='image', framerate=5, save_fig_at=None):
        warnings.warn("The makeImage function is deprecated and "
                      "will be removed in version 2.0.0. "
                      "Use the make_image function instead.",
                      FutureWarning,
                      stacklevel=8
                      )
        return self.make_image(linewidth, output_file, framerate, save_fig_at)

    def make_image(self, linewidth=0.5, output_file='image', framerate=5, save_fig_at=None):
        for axarr in self.axarr:
            axarr.lines = []

        frame = 1
        if save_fig_at is not None or 'Color' in self.track_df.df:
            if not isinstance(save_fig_at, list):
                # If it is not a list, make a list of one element
                save_fig_at = [save_fig_at]

            for point, next_point in self.compute_points(linewidth=linewidth):
                if self.is_new_frame(point, next_point):
                    second = frame / framerate
                    if second in save_fig_at:
                        plt.savefig(output_file + '_' + str(second) + '.png', facecolor=self.fig.get_facecolor())
                    frame = frame + 1
        else:
            self.compute_tracks(linewidth=linewidth)

        plt.savefig(output_file + '.png', facecolor=self.fig.get_facecolor())

    def isNewFrame(self, point, next_point):
        warnings.warn("The isNewFrame function is deprecated and "
                      "will be removed in version 2.0.0. "
                      "Use the is_new_frame function instead.",
                      FutureWarning,
                      stacklevel=8
                      )
        return self.is_new_frame(point, next_point)

    def is_new_frame(self, point, next_point):
        if next_point is not None:
            if 'VideoFrame' in point:
                new_frame = point['VideoFrame'] != next_point['VideoFrame']
            else:
                new_frame = point['Date'] != next_point['Date']
        else:
            new_frame = False

        return new_frame





