package com.example.tracknalert;



import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.graphics.Color;
import android.os.Handler;
import android.widget.TextView;
import android.widget.Toast;

import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.TileOverlay;
import com.google.android.gms.maps.model.TileOverlayOptions;
import com.google.maps.android.heatmaps.Gradient;
import com.google.maps.android.heatmaps.HeatmapTileProvider;


import okhttp3.Call;
import okhttp3.Callback;
import okhttp3.MediaType;
import okhttp3.MultipartBody;
import okhttp3.OkHttpClient;
import okhttp3.Request;
import okhttp3.RequestBody;
import okhttp3.Response;

import org.json.JSONArray;
import org.json.JSONException;
import org.json.JSONObject;

import java.io.IOException;
import java.io.InputStream;
import java.util.ArrayList;
import java.util.HashMap;
import java.util.List;
import java.util.Scanner;
import java.util.concurrent.TimeUnit;

import android.Manifest;
import android.app.AlertDialog;
import android.content.DialogInterface;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.location.Criteria;
import android.location.Location;
import android.location.LocationListener;
import android.location.LocationManager;
import android.os.Build;
import android.provider.Settings;
import android.os.Bundle;
import android.util.Log;

import androidx.core.app.NotificationCompat;
import androidx.fragment.app.FragmentActivity;

import com.google.android.gms.maps.CameraUpdateFactory;
import com.google.android.gms.maps.GoogleMap;
import com.google.android.gms.maps.OnMapReadyCallback;
import com.google.android.gms.maps.SupportMapFragment;
import com.google.android.gms.maps.model.LatLng;
import com.google.android.gms.maps.model.Marker;
import com.google.android.gms.maps.model.MarkerOptions;

public class MapsActivity extends FragmentActivity implements OnMapReadyCallback, LocationListener {
    final static int PERMISSION_ALL = 1;
    final static String[] PERMISSIONS = {android.Manifest.permission.ACCESS_COARSE_LOCATION,
            Manifest.permission.ACCESS_FINE_LOCATION};
    private GoogleMap mMap;
    MarkerOptions mo;
    Marker marker;
    LocationManager locationManager;
    String ipaddr = "192.168.1.101";
    String port = "5000";
    LatLng myCoordinates;
    double curr_lat,curr_long;
    String responseText,prevresponseText;
    int notif_id;
    double speed;

    @Override
    protected void onCreate(Bundle savedInstanceState) {
        super.onCreate(savedInstanceState);
        setContentView(R.layout.activity_maps);
        SupportMapFragment mapFragment = (SupportMapFragment) getSupportFragmentManager()
                .findFragmentById(R.id.map);
        mapFragment.getMapAsync(this);
        locationManager = (LocationManager) getSystemService(LOCATION_SERVICE);
        mo = new MarkerOptions().position(new LatLng(0, 0)).title("My Current Location");
        if (Build.VERSION.SDK_INT >= 23 && !isPermissionGranted()) {
            requestPermissions(PERMISSIONS, PERMISSION_ALL);
        } else requestLocation();
        if (!isLocationEnabled())
            showAlert(1);
        notif_id=0;
        responseText = "0";
        keepChecking();
    }

    private double getDistance(double lat1,double lat2,double lon1,double lon2)
    {
        double R = 6371e3; // metres
        double φ1 = lat1 * Math.PI/180; // φ, λ in radians
        double φ2 = lat2 * Math.PI/180;
        double Δφ = (lat2-lat1) * Math.PI/180;
        double Δλ = (lon2-lon1) * Math.PI/180;

        double a = Math.sin(Δφ/2) * Math.sin(Δφ/2) +
                    Math.cos(φ1) * Math.cos(φ2) *
                            Math.sin(Δλ/2) * Math.sin(Δλ/2);
        double c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));

        double d = R * c; // in metres
        return d;
    }

    @Override
    public void onMapReady(GoogleMap googleMap) {
        mMap = googleMap;
        marker =  mMap.addMarker(mo);
        addHeatMap();
    }

    double prev_lat,prev_long;

    @Override
    public void onLocationChanged(Location location) {

        prev_lat = curr_lat;
        prev_long=curr_long;
        myCoordinates = new LatLng(location.getLatitude(), location.getLongitude());
        curr_lat = location.getLatitude();
        curr_long = location.getLongitude();
        if(myCoordinates!=null)
        {
            marker.setPosition(myCoordinates);
            mMap.moveCamera(CameraUpdateFactory.newLatLng(myCoordinates));
        }


    }

    @Override
    public void onStatusChanged(String s, int i, Bundle bundle) {

    }

    @Override
    public void onProviderEnabled(String s) {

    }

    @Override
    public void onProviderDisabled(String s) {

    }


    private void notifyUser(int id)
    {   Log.d("Notif","Cslled");
        String textTitle = "Safety Alert";
        String textContent = "You are advised to drive cautiously in this region - watch out for pedestrians and speed-breakers";

        NotificationManager mNotificationManager;

        NotificationCompat.Builder mBuilder =
                new NotificationCompat.Builder(getApplicationContext(), "notify_001");
        Intent ii = new Intent(getApplicationContext(), Alert.class);
        PendingIntent pendingIntent = PendingIntent.getActivity(MapsActivity.this, 0, ii, 0);


        NotificationCompat.BigTextStyle bigText = new NotificationCompat.BigTextStyle();
        bigText.bigText(textContent);
        bigText.setBigContentTitle(textTitle);
        bigText.setSummaryText("Drive Cautiously!");

        mBuilder.setContentIntent(pendingIntent);
        mBuilder.setSmallIcon(R.mipmap.ic_launcher_round);
        mBuilder.setContentTitle(textTitle);
        mBuilder.setContentText(textContent);
        mBuilder.setPriority(Notification.PRIORITY_MAX);
        mBuilder.setStyle(bigText);


        mNotificationManager =
                (NotificationManager)getSystemService(Context.NOTIFICATION_SERVICE);

// === Removed some obsoletes
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O)
        {
            String channelId = "Your_channel_id";
            NotificationChannel channel = new NotificationChannel(
                    channelId,
                    "Channel human readable title",
                    NotificationManager.IMPORTANCE_HIGH);
            mNotificationManager.createNotificationChannel(channel);
            mBuilder.setChannelId(channelId);
        }

        mNotificationManager.notify(id, mBuilder.build());


    }

    private void checkAlert() {

        speed = getDistance(prev_lat,curr_lat,prev_long,curr_long)*60.0;
        String string_lat = Double.toString(curr_lat);
        String string_long = Double.toString(curr_long);
        String url = "http://" + ipaddr + ":" + port + "/Op/" + string_lat + "," + string_long + "," + Double.toString(speed);
        OkHttpClient client = new OkHttpClient().newBuilder()
                .connectTimeout(30, TimeUnit.SECONDS)
                .writeTimeout(30, TimeUnit.SECONDS)
                .readTimeout(30, TimeUnit.SECONDS)
                .build();
        Request request = new Request.Builder()
                .url(url)
                .build();

        client.newCall(request).enqueue(new Callback() {
            @Override
            public void onFailure(Call call, final IOException e) {
                call.cancel();
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {
                        Toast.makeText(MapsActivity.this,e.getMessage(),Toast.LENGTH_SHORT).show();
                    }
                });
            }

            @Override
            public void onResponse(Call call, final Response response) throws IOException {
                runOnUiThread(new Runnable() {
                    @Override
                    public void run() {

                        try {
                            prevresponseText = responseText;
                            responseText = response.body().string();
                            //Toast.makeText(MapsActivity.this,responseText,Toast.LENGTH_SHORT).show();
                            if(responseText.equals("1"))
                            {
                                if(prevresponseText.equals("0"))
                                {
                                    notif_id+=1;
                                    notifyUser(notif_id);
                                    startActivity(new Intent(MapsActivity.this,Alert.class));
                                }

                            }
                        } catch (IOException e) {
                            Toast.makeText(MapsActivity.this,e.getMessage(),Toast.LENGTH_SHORT).show();

                        }
                    }
                });
            }
        });

    }


    private void keepChecking() {
        final Handler handler = new Handler();
        handler.postDelayed(new Runnable() {
            @Override
            public void run() {
                checkAlert();
                handler.postDelayed(this, 1000*10);
            }
        }, 1000*30);



    }

    private void requestLocation() {
        Criteria criteria = new Criteria();
        criteria.setAccuracy(Criteria.ACCURACY_FINE);
        criteria.setPowerRequirement(Criteria.POWER_HIGH);
        String provider = locationManager.getBestProvider(criteria, true);
        locationManager.requestLocationUpdates(provider, 10000, 10, this);
    }
    private boolean isLocationEnabled() {
        return locationManager.isProviderEnabled(LocationManager.GPS_PROVIDER) ||
                locationManager.isProviderEnabled(LocationManager.NETWORK_PROVIDER);
    }

    private boolean isPermissionGranted() {
        if (checkSelfPermission(android.Manifest.permission.ACCESS_COARSE_LOCATION)
                == PackageManager.PERMISSION_GRANTED || checkSelfPermission(android.Manifest.permission.ACCESS_FINE_LOCATION)
                == PackageManager.PERMISSION_GRANTED) {
            Log.v("mylog", "Permission is granted");
            return true;
        } else {
            Log.v("mylog", "Permission not granted");
            return false;
        }
    }
    private void showAlert(final int status) {
        String message, title, btnText;
        if (status == 1) {
            message = "Your Locations Settings is set to 'Off'.\nPlease Enable Location to " +
                    "use this app";
            title = "Enable Location";
            btnText = "Location Settings";
        } else {
            message = "Please allow this app to access location!";
            title = "Permission access";
            btnText = "Grant";
        }
        final AlertDialog.Builder dialog = new AlertDialog.Builder(this);
        dialog.setCancelable(false);
        dialog.setTitle(title)
                .setMessage(message)
                .setPositiveButton(btnText, new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface paramDialogInterface, int paramInt) {
                        if (status == 1) {
                            Intent myIntent = new Intent(Settings.ACTION_LOCATION_SOURCE_SETTINGS);
                            startActivity(myIntent);
                        } else
                            requestPermissions(PERMISSIONS, PERMISSION_ALL);
                    }
                })
                .setNegativeButton("Cancel", new DialogInterface.OnClickListener() {
                    @Override
                    public void onClick(DialogInterface paramDialogInterface, int paramInt) {
                        finish();
                    }
                });
        dialog.show();
    }


    private void addHeatMap() {
        List<LatLng> list = null;

        // Get the data: latitude/longitude positions of police stations.
        try {
            list = readItems(R.raw.coords);
        } catch (JSONException e) {
            Toast.makeText(this, "Problem reading list of locations.", Toast.LENGTH_LONG).show();
        }


        int[] colors = {
                Color.rgb(102, 225, 0), // green
                Color.rgb(255, 0, 0) ,// red

        };

        float[] startPoints = {
                0.2f, 0.4f
        };

        Gradient gradient = new Gradient(colors, startPoints);


        // Create a heat map tile provider, passing it the latlngs of the police stations.
        HeatmapTileProvider mProvider = new HeatmapTileProvider.Builder()
                .data(list)
                .gradient(gradient)
                .opacity(1)
                .build();
        // Add a tile overlay to the map, using the heat map tile provider.
        TileOverlay mOverlay = mMap.addTileOverlay(new TileOverlayOptions().tileProvider(mProvider));
    }

    private ArrayList<LatLng> readItems(int resource) throws JSONException {
        ArrayList<LatLng> list = new ArrayList<LatLng>();
        InputStream inputStream = getResources().openRawResource(resource);
        String json = new Scanner(inputStream).useDelimiter("\\A").next();
        JSONArray array = new JSONArray(json);
        Log.d("Coords",Integer.toString(array.length()));
        for (int i = 0; i < array.length(); i++) {
            JSONObject object = array.getJSONObject(i);
            double lat = object.getDouble("lat");
            double lng = object.getDouble("lng");
            list.add(new LatLng(lat, lng));
        }
        return list;
    }

}

